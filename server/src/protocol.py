from twisted.internet.protocol import Factory
from twisted.protocols import amp

import exceptions
from actions import (
    create_player, increase_score, move_player, restart_round, revive_player, shoot_action
)
from game_commands import (
    Move, MoveObject, SendMap, CreateObject, CreateObjects, Login, PlayerShoot, Shoot, PlayerHit,
    PlayerRevive, LogoutPlayer, UpdateScore, RestartRound
)


class PWProtocolFactory(Factory):
    def __init__(self):
        self.peers = {}

    def buildProtocol(self, addr):
        return PWProtocol(self)


class PWProtocol(amp.AMP):
    hcriat = None

    def __init__(self, factory):
        self.factory = factory

    def connectionLost(self, reason):
        player = self.factory.peers.pop(self)
        self.hcriat.del_creature_by_uid(player.uid)
        self.send_client(LogoutPlayer, broadcast=True, uid=player.uid)

    def connectionMade(self):
        self.transport.setTcpNoDelay(True)

    def send_client(self, command_type, *a, **kw):
        peers = [self]
        if 'broadcast' in kw:
            peers = self.factory.peers.keys()
            del kw['broadcast']
        for peer in peers:
            peer.callRemote(command_type, *a, **kw)

    @Move.responder
    def move(self, uid, direction):
        try:
            jug = move_player(uid, direction, self.hcriat)
        except (exceptions.BlockedPosition, exceptions.CantMove):
            pass
        else:
            self.send_client(MoveObject, broadcast=True, uid=uid, x=jug.x, y=jug.y)
        return {'ok': 1}

    @Login.responder
    def login(self, team):
        player, other_players, score, pw_map = create_player(team, self.hcriat)
        self.factory.peers[self] = player
        # map
        self.send_client(SendMap, sec_map=pw_map.array_map)
        # create new player on all the clients
        self.send_client(CreateObject, broadcast=True, obj_data=player.get_data())
        # create all the players on the new client
        self.send_client(CreateObjects, obj_data=[p.get_data() for p in other_players])
        # update the score
        self.send_client(UpdateScore, blue=score[0], red=score[1])
        return {'uid': player.uid}

    @Shoot.responder
    def player_shoot(self, uid, direction):
        try:
            jug, shoot_handler = shoot_action(uid, direction, self.hcriat, self.hit, self.die)
        except exceptions.CantShoot:
            pass
        else:
            self.send_client(
                PlayerShoot, broadcast=True, uid=uid, direction=direction, x=jug.x, y=jug.y
            )
        return {'ok': 1}

    @RestartRound.responder
    def restart_round(self, uid):
        players, new_score = restart_round(uid, self.hcriat)
        self.send_client(UpdateScore, broadcast=True, blue=new_score[0], red=new_score[1])
        for p in players:
            self.send_client(MoveObject, broadcast=True, uid=p.uid, x=p.x, y=p.y)
            self.send_client(PlayerRevive, broadcast=True, uid=p.uid)
        return {'ok': 1}

    def hit(self, player_uid, damage):
        self.send_client(PlayerHit, broadcast=True, uid=player_uid, dmg=damage)

    def die(self, player_uid):
        score = increase_score(player_uid, self.hcriat)
        revive_player(player_uid, self.hcriat)
        self.send_client(PlayerRevive, broadcast=True, uid=player_uid)
        self.send_client(UpdateScore, broadcast=True, blue=score[0], red=score[1])
