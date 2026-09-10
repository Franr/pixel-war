import asyncio
import signal
from typing import Any

from shared.commands import (
    Command,
    CreateObject,
    CreateObjects,
    MoveObject,
    PlayerHit,
    PlayerLogout,
    PlayerRevive,
    PlayerShoot,
    SendMap,
    ServerError,
    UpdateScore,
)
from shared.protocol import MessageProtocol

from .actions import (
    create_player,
    increase_score,
    move_player,
    revive_player,
    shoot_action,
)
from .exceptions import BlockedPosition, CantMove, CantShoot, RespawnFull
from .handlers import BulletHandler, CreaturesHandler
from .logger import logger
from .mapa import Mapa
from .score import Score

# class Commands:

    # # @RestartRound.responder
    # def restart_round(self, uid):
    #     players, new_score = restart_round(uid, self.ch)
    #     self.send_client(UpdateScore, broadcast=True, blue=new_score[0], red=new_score[1])
    #     for p in players:
    #         self.send_client(MoveObject, broadcast=True, uid=p.uid, x=p.x, y=p.y)
    #         self.send_client(PlayerRevive, broadcast=True, uid=p.uid)
    #     return self.OK_OBJ

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
        logger.debug(f"Message: {message!r}")
        for client in self.clients.values():
            client.send_message(message)

    async def start(self):
        loop = asyncio.get_running_loop()
        self.async_server = await loop.create_server(
            lambda: Server(self.clients, self.gh),
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


class GameHandler:

    def __init__(self, server: ServerHandler):
        self.pw_map = Mapa("mapa")
        self.score = Score()
        self.ch = CreaturesHandler()
        self.ch.pw_map = self.pw_map  # TODO: move as CreaturesHandler argument
        self.ch.score = self.score
        self.peers: dict[tuple[str, int], int] = {}
        self.server = server

    def command_dispatcher(self, client, command: str, payload: dict, extra: dict[str, Any]|None = None):
        extra = extra or {}
        return getattr(self, command)(client, **dict(payload, **extra))

    def broadcast(self, cmd: Command):
        self.server.broadcast(cmd)

    def login(self, client, team: int, correlation_id: str) -> dict[str, int]:
        player_uid = -1  # replaced if the player creation is successful
        try:
            # create player
            player, other_players, score, pw_map = create_player(team, self.ch)
            player_uid = player.uid
        except RespawnFull:
            client.send_message(ServerError(description=RespawnFull.details))
        else:
            # map
            client.send_message(SendMap(sec_map=pw_map.array_map))
            # create new player on all the clients
            self.broadcast(CreateObject(obj_data=player.get_data(), correlation_id=correlation_id))
            # create all the players on the new client
            client.send_message(CreateObjects(objs_data=[p.get_data() for p in other_players]))
            # update the score
            client.send_message(UpdateScore(blue=score[0], red=score[1]))

        # associate ip/port with uid, for the logout case
        self.peers[client.address] = player_uid
        
        return {'uid': player_uid}

    def move(self, client, uid: int, direction: str):
        try:
            jug = move_player(uid, direction, self.ch)
        except (BlockedPosition, CantMove):
            return False
        else:
            self.broadcast(MoveObject(uid=uid, x=jug.x, y=jug.y))

        return True

    def shoot(self, client, uid: int, direction: str):
        try:
            bh: BulletHandler = shoot_action(uid, direction, self.ch, self._hit_callback, self._die_callback)
        except CantShoot:
            return False
        else:
            self.broadcast(PlayerShoot(uid=uid, direction=direction, x=bh.jug.x, y=bh.jug.y))

        return True

    def _hit_callback(self, uid: int, damage: int) -> bool:
        """
        Callback when a player get hitted: substract life.
        """
        self.broadcast(PlayerHit(uid=uid, dmg=damage))

        return True

    def _die_callback(self, uid: int) -> bool:
        """
        Callback when a player die: revive it and update score.
        """
        score = increase_score(uid, self.ch)
        revive_player(uid, self.ch)
        self.broadcast(PlayerRevive(uid=uid))
        self.broadcast(UpdateScore(blue=score[0], red=score[1]))

        return True


class Server(MessageProtocol):
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
        uid = self.gh.peers.pop(self.address)
        self.gh.broadcast(PlayerLogout(uid=uid))
        logger.info(f"[SERVER] Client disconnected: {self.address} - Player ID: {uid}")

    def message_received(self, message: dict):
        action = message.pop("action")
        result = self.gh.command_dispatcher(self, action, message)
        logger.debug(f"[MessageReceived] From: {self.address} - Action:{action} - Message:{message} - Result:{result}]")
