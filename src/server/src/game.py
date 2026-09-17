from typing import TYPE_CHECKING

from shared.commands import (
    Command,
    CreateObject,
    CreateObjects,
    Login,
    MoveObject,
    PlayerHit,
    PlayerLogout,
    PlayerRevive,
    PlayerShoot,
    SendMap,
    ServerError,
    UpdateScore,
)

if TYPE_CHECKING:
    from .server import Connection, ServerHandler

from .actions import (
    create_player,
    increase_score,
    move_player,
    restart_round,
    revive_player,
    shoot_action,
)
from .exceptions import (
    BlockedPosition,
    CantMove,
    CantShoot,
    InvalidTeam,
    PlayerDoesNotExist,
    RespawnFull,
)
from .handlers import BulletHandler, CreaturesHandler
from .logger import logger
from .mapa import Mapa
from .score import Score


class GameHandler:

    INVALID_UID_PLAYER = -1

    def __init__(self, server: "ServerHandler"):
        self.pw_map = Mapa("mapa")
        self.score = Score()
        self.ch = CreaturesHandler()
        self.ch.pw_map = self.pw_map  # TODO: move as CreaturesHandler argument
        self.ch.score = self.score
        self.peers: dict[tuple[str, int], int] = {}
        self.server = server

    def command_dispatcher(self, client: "Connection", command: str, payload: dict):
        if command != Login.action and self.peers[client.address] == self.INVALID_UID_PLAYER:
            # messages coming from a not yet logged in player, ignore them
            logger.warning(f"{client.address} sending {command}. Ignored.")
            return

        return getattr(self, command)(client, **dict(payload))

    def broadcast(self, cmd: Command):
        self.server.broadcast(cmd)

    def login(self, client: "Connection", team: int, correlation_id: str) -> int:
        player_uid = self.INVALID_UID_PLAYER  # replaced if the player creation is successful
        try:
            # create player
            player, other_players, score, pw_map = create_player(team, self.ch)
            player_uid = player.uid
        except RespawnFull:
            client.send_message(ServerError(description=RespawnFull.details))
        except InvalidTeam:
            client.send_message(ServerError(description=InvalidTeam.details))
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

        return player_uid

    def move(self, client: "Connection", uid: int, direction: str) -> bool:
        try:
            jug = move_player(uid, direction, self.ch)
        except (BlockedPosition, CantMove, PlayerDoesNotExist):
            return False
        else:
            self.broadcast(MoveObject(uid=uid, x=jug.x, y=jug.y))

        return True

    def shoot(self, client: "Connection", uid: int, direction: str) -> bool:
        try:
            bh: BulletHandler = shoot_action(uid, direction, self.ch, self._hit_callback, self._die_callback)
        except (CantShoot, PlayerDoesNotExist):
            return False
        else:
            self.broadcast(PlayerShoot(uid=uid, direction=direction, x=bh.jug.x, y=bh.jug.y))

        return True

    def restart_round(self) -> bool:
        """
        Player requested to restart the round.
        """
        try:
            players, new_score = restart_round(self.ch)
        except PlayerDoesNotExist:
            return False
        else:
            self.broadcast(UpdateScore(blue=new_score[0], red=new_score[1]))
            for p in players:
                self.broadcast(MoveObject(uid=p.uid, x=p.x, y=p.y))
                self.broadcast(PlayerRevive(uid=p.uid))

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

    def logout(self, address: tuple[str, int]):
        uid = self.peers.pop(address)
        self.ch.del_creature_by_uid(uid)
        self.broadcast(PlayerLogout(uid=uid))

        return uid
