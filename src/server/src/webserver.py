import asyncio
from dataclasses import asdict
from json import JSONDecodeError

from shared.commands import Command
from shared.protocol import json
from websockets.asyncio.server import ServerConnection, serve

from .game import GameHandler
from .logger import logger


class WebSocketServerHandler:
    """
    Manage starting and stoping websocket server, connections and incoming/outgoing messages.
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
        self.ws_server = await serve(self.handler, self.host, self.port)
        logger.info(f"Server listening on ws://{self.host}:{self.port}")
        await self.ws_server.serve_forever()

    async def connection_handler(self, websocket):
        async for message in websocket:
            if websocket.remote_address not in self.clients:
                # register connection
                logger.info(f"{websocket.id} joined")
                connection = Connection(websocket, self.clients, self.gh)
            else:
                connection = self.clients.get(websocket.remote_address)

            # parse and dispatch
            try:
                msg = json.loads(message)
            except JSONDecodeError:
                logger.warning(f"Invalid JSON message: {message}")
            else:
                self.dispatch(connection, msg)

    async def handler(self, websocket):
        try:
            await self.connection_handler(websocket)
        # TODO: ConnectionClosed/exceptions handlers
        finally:
            # connection closed
            # if not websocket.remote_address in self.clients:
                # return
            self.clients.pop(websocket.remote_address)
            uid = self.gh.logout(websocket.remote_address)
            logger.info(f"[SERVER] Client disconnected: {websocket.remote_address} - Player ID: {uid}")

    def close_client_connections(self):
        print("closing server")
        self.ws_server.close()
        print("done!")

    def dispatch(self, client, message):
        action = message.pop("action")
        result = self.gh.command_dispatcher(client, action, message)
        logger.debug(f"[MsgRcvd] F:{client.address} - A:{action} - M:{message} - R:{result}]")

    async def run(self):
        print("starting server")
        await self.start()


class Connection:
    """
    Handles client connection. 1 instance per client connected.
    """
    def __init__(self, websocket: ServerConnection, clients, game_handler: GameHandler):
        super().__init__()
        self.websocket = websocket
        self.clients = clients  # shared with ServerHandler
        self.gh = game_handler
        self.clients[self.address] = self
        logger.info(f"[SERVER] Client connected: {self.address}")

    @property
    def address(self) -> str:
        return self.websocket.remote_address

    def send_message(self, data: Command):
        loop = asyncio.get_running_loop()
        message = json.dumps(asdict(data))
        asyncio.run_coroutine_threadsafe(self.websocket.send(message), loop)
