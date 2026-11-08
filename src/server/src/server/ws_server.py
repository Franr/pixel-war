import asyncio
from dataclasses import asdict
from json import JSONDecodeError

from shared.commands import Command
from shared.protocol import json
from websockets.asyncio.server import ServerConnection, serve

from src.server.base import BaseConnection, BaseServerHandler

from ..game import GameHandler
from ..logger import logger


class WebSocketServerHandler(BaseServerHandler):
    """
    Manage starting and stopping websocket server, connections and incoming/outgoing messages.
    """

    async def connection_handler(self, websocket):
        async for message in websocket:
            if websocket.remote_address not in self.clients:
                # register connection
                logger.info(f"{websocket.id} joined")
                connection = WSConnection(websocket, self.clients, self.gh)
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
            client = self.clients.pop(websocket.remote_address, None)
            if not client:
                # connected but never joined the game
                uid = self.gh.INVALID_UID_PLAYER
            else:
                uid = self.gh.logout(websocket.remote_address)

            logger.info(f"[SERVER] Client disconnected: {websocket.remote_address} - Player ID: {uid}")

    def close_server(self):
        logger.info("Closing websocket server...")
        self.ws_server.close()
        logger.info("Closed.")

    def dispatch(self, client, message):
        action = message.pop("action")
        result = self.gh.command_dispatcher(client, action, message)
        logger.debug(f"[MsgRcvd] F:{client.address} - A:{action} - M:{message} - R:{result}]")

    async def run(self):
        self.ws_server = await serve(self.handler, self.host, self.port)
        logger.info(f"Server listening on ws://{self.host}:{self.port}")
        await self.ws_server.serve_forever()


class WSConnection(BaseConnection):
    """
    Handles client connection. 1 instance per client connected.
    """
    def __init__(self, websocket: ServerConnection, clients, game_handler: GameHandler):
        super().__init__(clients, game_handler)
        self.websocket = websocket
        self.register_client()
        logger.info(f"[SERVER] Client connected: {self.address}")

    @property
    def address(self) -> tuple:
        return self.websocket.remote_address

    def send_message(self, data: Command):
        loop = asyncio.get_running_loop()
        message = json.dumps(asdict(data))
        asyncio.run_coroutine_threadsafe(self.websocket.send(message), loop)
