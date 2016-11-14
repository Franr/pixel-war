class Positionable(object):

    def __init__(self, x, y):
        self.x, self.y = x, y

    def get_coor(self):
        return self.x, self.y

    def update(self, x, y):
        self.x, self.y = x, y


class HandlerCreatures(object):

    def __init__(self):
        self.my_team = None
        self.azul = 0
        self.rojo = 0
        self.jugadores = {}

    def create_player(self, uid, x, y, vida, vida_max, equipo):
        player = Player(uid, x, y, vida, vida_max, equipo)
        self.jugadores[player.get_uid()] = player
        return player

    def get_players(self):
        return self.jugadores.values()

    def get_enemies(self):
        return [j for j in self.jugadores.values() if j.equipo != self.my_team]

    def get_creature_by_uid(self, uid):
        if uid in self.jugadores:
            return self.jugadores[uid]
        else:
            print("Id invalida:" + str(uid))

    def del_creature_by_id(self, uid):
        if uid in self.jugadores:
            return self.jugadores.pop(uid)
        else:
            print("Id invalida:" + str(uid))

    def reset_all(self):
        for j in self.jugadores.values():
            j.reset()

    def set_score(self, azul, rojo):
        self.azul = azul
        self.rojo = rojo


class Creature(Positionable):

    def __init__(self, uid, x, y, vida, vida_max, equipo):
        super(Creature, self).__init__(x, y)
        self.uid = uid
        self.vida = Vida(vida, vida_max)
        self.equipo = equipo
        self.vivo = True

    def get_uid(self):
        return self.uid

    def es_id(self, uid):
        return self.uid == uid

    def get_equipo(self):
        return self.equipo

    def es_equipo(self, equipo):
        return self.equipo == equipo

    def get_vida(self):
        return self.vida.get()

    def reset(self):
        self.vivo = True
        self.vida.llenar()

    def esta_vivo(self):
        return self.vivo

    def hit(self, danio):
        self.vida.hit(danio)

    def mover(self, x, y):
        self.update(x, y)

    def matar(self):
        self.vivo = False


class Player(Creature):

    def __init__(self, uid, x, y, vida, vida_max, team):
        super(Player, self).__init__(uid, x, y, vida, vida_max, team)
        self.es_principal = False


class Vida(object):

    def __init__(self, hp, max_hp):
        self.actual, self.max = hp, max_hp

    def hit(self, cant):
        if self.actual - cant <= 0:
            self.actual = 0
        else:
            self.actual -= cant

    def llenar(self):
        self.actual = self.max

    def get(self):
        return self.actual
