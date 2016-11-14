from twisted.protocols import amp

from game_commands import (
    Move, MoveObject, SendMap, CreateObject, CreateObjects, Login, PlayerShoot, Shoot, PlayerHit,
    PlayerRevive, LogoutPlayer, UpdateScore, RestartRound, AddBot, DeleteBot)

from bala import Bullet
from bloqueos import FireBlock, MoveBlock


class PWProtocol(amp.AMP):

    def __init__(self, juego=None, hcriat=None, team=None):
        super(PWProtocol, self).__init__()
        self.juego = juego
        self.hcriat = hcriat
        self.team = team
        self.mapa = None
        self.my_uid = None
        self.move_blocker = MoveBlock()
        self.fire_blocker = FireBlock()

    def connectionMade(self):
        self.transport.setTcpNoDelay(True)
        self.callRemote(Login, team=self.team).addCallback(self.set_main_player)

    def set_main_player(self, result):
        self.my_uid = result['uid']
        principal = self.hcriat.get_creature_by_uid(self.my_uid)
        principal.es_principal = True
        self.juego.set_principal(principal)
        self.juego.activate_io_handlers()

    @CreateObject.responder
    def create_object(self, obj_data):
        uid, equipo, x, y, vida, vida_max = obj_data
        player = self.hcriat.create_player(uid, x, y, vida, vida_max, equipo)
        self.mapa.set_creature(player, player.x, player.y)
        print 'jugador creado:', uid, "en:", x, y
        return {'ok': 1}

    @CreateObjects.responder
    def create_objects(self, obj_data):
        for player_data in obj_data:
            self.create_object(player_data)
        return {'ok': 1}

    @SendMap.responder
    def send_map(self, sec_map):
        # receiving map on client
        self.mapa = self.juego.create_map(sec_map)
        return {'ok': 1}

    @MoveObject.responder
    def move_object(self, uid, x, y):
        # movemos el objeto
        criat = self.hcriat.get_creature_by_uid(uid)
        if criat:
            self.mapa.move_creature(criat, x, y)
            criat.mover(x, y)
        return {'ok': 1}

    @PlayerShoot.responder
    def player_shoot(self, uid, direction, x, y):
        # disparo
        jug = self.hcriat.get_creature_by_uid(uid)
        if jug:
            self.juego.add_bullet(Bullet(uid, x, y, direction, jug.get_equipo(), self.juego))
        return {'ok': 1}

    @PlayerHit.responder
    def hit(self, uid, dmg):
        jugador = self.hcriat.get_creature_by_uid(uid)
        if jugador:
            jugador.hit(dmg)
        return {'ok': 1}

    @PlayerRevive.responder
    def revive_player(self, uid):
        jugador = self.hcriat.get_creature_by_uid(uid)
        if jugador:
            jugador.reset()
        return {'ok': 1}

    @LogoutPlayer.responder
    def logout_player(self, uid):
        self.logout(uid)
        return {'ok': 1}

    @UpdateScore.responder
    def update_score(self, blue, red):
        self.hcriat.set_score(blue, red)
        return {'ok': 1}

    def fire(self, direction):
        if not self.fire_blocker.is_blocked():
            self.callRemote(Shoot, uid=self.my_uid, direction=direction)
            self.fire_blocker.block()

    def logout(self, uid):
        # desconectar
        jug = self.hcriat.get_creature_by_uid(uid)
        if jug:
            self.mapa.clean_position(jug.x, jug.y)
            self.hcriat.del_creature_by_id(uid)

    def move(self, direction):
        if not self.move_blocker.is_blocked():
            self.callRemote(Move, uid=self.my_uid, direction=direction)
            self.move_blocker.block()

    def restart_round(self):
        self.callRemote(RestartRound, uid=self.my_uid)

    def add_bot(self, team):
        self.callRemote(AddBot, team=team)

    def delete_bot(self, team):
        self.callRemote(DeleteBot, team=team)
