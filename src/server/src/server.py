import asyncio
import signal

from shared.commands import Command
from shared.protocol import MessageProtocol

from .game import GameHandler
from .logger import logger


class ServerHandler:
    """
    Manage starting and stoping server, connections and incoming/outgoing messages
    # """

    def __init__(self, host="127.0.0.1", port=8888) -> None:
        self.host = host
        self.port = port
        self.clients = {}
        self.gh = GameHandler(self)

    def broadcast(self, message: Command):
        logger.debug(f"[BrdCst ] M:{message}")

        for client in self.clients.values():
            client.send_message(message)

    async def start(self):
        loop = asyncio.get_running_loop()
        self.async_server = await loop.create_server(
            lambda: Connection(self.clients, self.gh),
            self.host,
            self.port
        )
        logger.info(f"Server listening on {self.host}:{self.port}")
        await self.async_server.serve_forever()

    async def stop(self):
        logger.info("Initiating graceful server shutdown...")

        # Close all active client connections cleanly
        for client in self.clients.values():
            client.transport.close()
        self.clients.clear()

        # Stop accepting new connections and close the server socket
        self.async_server.close()
        await self.async_server.wait_closed()

        logger.info("Server shut down successfully.")

    async def run(self):
        loop = asyncio.get_running_loop()
        stop_event = asyncio.Event()
    
        def handle_signal():
            logger.info("Shutdown signal received.")
            stop_event.set()
    
        # Attach signal handlers for graceful shutdown (Unix/Linux/macOS)
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, handle_signal)
            except NotImplementedError:
                # Signal handling on Windows (fallback via KeyboardInterrupt handling)
                pass
    
        server_task = asyncio.create_task(self.start())
    
        # Wait until a termination signal is triggered
        await stop_event.wait()
        
        # Cancel the server loop and run cleanup
        server_task.cancel()
        await self.stop()


class Connection(MessageProtocol):
    """
    Handles client connection. 1 instance per client connected.
    """
    def __init__(self, clients, game_handler: GameHandler):
        super().__init__()
        self.clients = clients  # shared with ServerHandler
        self.gh = game_handler

    @property
    def address(self) -> tuple[str, int]:
        """
        Returns ip and port.
        e.g.: ("127.0.0.1", 50023)
        """
        return self.transport.get_extra_info("peername")

    def connection_made(self, transport):
        super().connection_made(transport)
        self.clients[self.address] = self
        logger.info(f"[SERVER] Client connected: {self.address}")

    def connection_lost(self, exc):
        if not self.address in self.clients:
            return

        self.clients.pop(self.address)
        uid = self.gh.logout(self.address)
        logger.info(f"[SERVER] Client disconnected: {self.address} - Player ID: {uid}")

    def message_received(self, message: dict):
        action = message.pop("action")
        result = self.gh.command_dispatcher(self, action, message)
        logger.debug(f"[MsgRcvd] F:{self.address} - A:{action} - M:{message} - R:{result}]")
