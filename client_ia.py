#!/usr/bin/env python

from client.mapa import MapLogic
from ia.ia import avoid_shoot, shoot_enemy, move
from client_ui import Juego


class Bot(Juego):

    def load_io_handlers(self):
        pass

    def update(self):
        avoid_shoot(self.principal, self.balas.balas, self.conexion)
        shoot_enemy(self.principal, self.hcriat.get_enemies(), self.conexion)
        move(self.principal, self.conexion)

    def activate_io_handlers(self):
        pass

    def set_principal(self, jugador):
        self.principal = jugador
        self.hcriat.my_team = jugador.equipo

    def create_map(self, sequence):
        return MapLogic(sequence)


if __name__ == '__main__':
    team = input('1 - blue ; 2 - red\n')
    ip = raw_input('IP: (default is 127.0.0.1)\n') or '127.0.0.1'
    Bot(ip, team)
