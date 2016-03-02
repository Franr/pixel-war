import os

import exceptions
from utils import Archivo


class Mapa(object):

    # Dividir en 2 clases:
    # el mapa y el handler del mapa

    # atencion:
    # internamente la clase maneja las coordenadas primero a "Y" y despues a "X"
    # por la manera en que se splitea el mapa desde el archivo.
    # pero las llamadas a los metodos desde afuera se hace igual que siempre: x, y.

    # El mapa solo contiene ids en sus arrays:
    # = 0  libre
    # = 1  bloque
    # > 1  jugador

    def __init__(self, nombre):
        self.nombre = nombre
        self.array_map = []
        # team respawn
        self.x_rojo, self.y_rojo, self.x_azul, self.y_azul = None, None, None, None
        # medidas del mapa
        self.dy = 0
        self.dx = 0
        # cargamos los mapas numericos
        maps_folder = os.path.dirname(__file__) + '/../maps'
        sec = self.parse(Archivo(maps_folder, nombre + ".pwm", "r").buffer)
        if sec:
            self.gen_mapa_numerico(sec)

    def parse(self, sec):
        # Dividimos c/linea por las comas
        for i in range(len(sec)):
            sec[i] = sec[i].split(',')

        # calculamos las medidas del mapa:
        self.dy = len(sec)
        self.dx = len(sec[0])
        return sec

    def gen_mapa_numerico(self, mapa):
        for y in range(len(mapa)):
            row = []
            for x in range(len(mapa[y])):
                mid = int(mapa[y][x])
                if mid == 2:
                    # respawn rojo
                    self.set_red(x, y)
                    mid = 0
                elif mid == 3:
                    # respawn azul
                    self.set_azul(x, y)
                    mid = 0
                row.append(mid)
            self.array_map.append(row)

    def get_id_by_pos(self, x, y):
        return self.array_map[y][x]

    def set_object(self, objeto, x, y):
        self.array_map[y][x] = objeto.get_uid()

    def set_red(self, x, y):
        self.x_rojo = x
        self.y_rojo = y

    def set_azul(self, x, y):
        self.x_azul = x
        self.y_azul = y

    def get_red(self):
        if self.pos_is_blocked(self.x_rojo, self.y_rojo):
            return self.get_empty_place(self.x_rojo, self.y_rojo)
        else:
            return self.x_rojo, self.y_rojo

    def get_blue(self):
        if self.pos_is_blocked(self.x_azul, self.y_azul):
            return self.get_empty_place(self.x_azul, self.y_azul)
        else:
            return self.x_azul, self.y_azul

    def base_position(self, jugador):
        pos = None
        if jugador.get_team() == 1:  # TODO: check team reference
            pos = self.get_blue()
        elif jugador.get_team() == 2:
            pos = self.get_red()

        x, y = pos
        self.set_object(jugador, x, y)
        jugador.mover(x, y)
        return jugador

    def del_object(self, entity):
        self.clean_coor(*entity.get_coor())

    def clean_coor(self, x, y):
        self.array_map[y][x] = 0

    def pos_is_blocked(self, x, y):
        return self.array_map[y][x] >= 1

    def get_empty_place(self, x, y):
        cuadrante = [[-1, -1], [0, -1], [1, -1],
                     [-1,  0],          [1,  0],
                     [-1,  1], [0,  1], [1,  1]]

        for pos in cuadrante:
            nx = x + pos[0]
            ny = y + pos[1]
            if not self.pos_is_blocked(nx, ny):
                return nx, ny
        raise exceptions.TeamBasePositionNotFound

    def move_player(self, jugador, x, y):
        antx, anty = jugador.get_coor()
        jugador.mover(x, y)
        self.clean_coor(antx, anty)
        self.set_object(jugador, x, y)

    def clean_map(self):
        for y in range(len(self.array_map)):
            for x in range(len(self.array_map[y])):
                if self.array_map[y][x] != 1:
                    self.array_map[y][x] = 0
