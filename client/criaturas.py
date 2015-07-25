import pygame


class Objeto(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = self.get_rect()

    def get_coor(self):
        return self.x, self.y

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 7, 7)

    def update(self, x, y):
        self.x = x
        self.y = y

    def colisiona(self, rects):
        return self.rect.collidelist(rects) != -1


class HandlerCriaturas(object):

    def __init__(self):
        self.azul = 0
        self.rojo = 0
        self.ronda = 0
        self.jugadores = {}
        self.enemigos = {}

    def add_player(self, jugador):
        self.jugadores[jugador.get_uid()] = jugador
        
    def add_enemy(self, enemigo):
        self.enemigos[enemigo.get_uid()] = enemigo
        
    def get_players(self):
        return self.jugadores.values()
        
    def get_enemies(self):
        return self.enemigos.values()
              
    def get_creature_by_uid(self, uid):
        if uid in self.jugadores:
            return self.jugadores[uid]
        elif uid in self.enemigos:
            return self.enemigos[uid]
        else:
            print("Id invalida:" + str(uid))
            return None

    def del_creature_by_id(self, uid):
        if uid in self.jugadores:
            self.jugadores.pop(uid)
        elif uid in self.enemigos:
            self.enemigos.pop(uid)
        else:
            print("Id invalida:" + str(uid))

    def reset_all(self):
        [j.reset() for j in self.jugadores.values()]

    def set_score(self, azul, rojo, ronda):
        self.azul = azul
        self.rojo = rojo
        self.ronda = ronda


class Criatura(Objeto):

    def __init__(self, uid, x, y, vida, vida_max, equipo):
        Objeto.__init__(self, x, y)
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

    def es_principal(self):
        return False

    def esta_vivo(self):
        return self.vivo

    def hit(self, danio):
        self.vida.hit(danio)

    def mover(self, x, y):
        self.update(x, y)

    def matar(self):
        self.vivo = False


class Jugador(Criatura):

    def __init__(self, uid, x, y, vida, vida_max, equipo):
        Criatura.__init__(self, uid, x, y, vida, vida_max, equipo)
        self.es_principal = False

    def es_principal(self):
        return self.es_principal


class Vida(object):

    def __init__(self, hp, max_hp):
        self.max = max_hp
        self.actual = hp

    def hit(self, cant):
        if self.actual - cant <= 0:
            self.actual = 0
        else:
            self.actual -= cant

    def llenar(self):
        self.actual = self.max

    def get(self):
        return self.actual
