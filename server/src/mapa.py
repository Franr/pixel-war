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
        self.mapaChar = None
        # cargamos los mapas numericos
        maps_folder = os.path.dirname(__file__) + '/../maps'
        sec = self.parse(Archivo(maps_folder, nombre + ".pwm", "r").buffer)
        if sec:
            self.gen_mapa_numerico(sec)
            self.gen_mapa_char()

    def parse(self, sec):
        # Dividimos c/linea por las comas
        for i in range(len(sec)):
            sec[i] = sec[i].split(',')

        # calculamos las medidas del mapa:
        self.dy = len(sec)
        self.dx = len(sec[0])
        return sec

    def gen_mapa_numerico(self, mapa):
        self.dicMapa = {}
        self.compacto = []
        for y in range(len(mapa)):
            fila_compacta = ""
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
                self.dicMapa[y, x] = mid
                fila_compacta += str(mid)
            # el compacto se usa para enviar el mapa en formato binario
            self.compacto.append(fila_compacta)

    def get_id_by_pos(self, x, y):
        return self.dicMapa[y, x]

    def set_object(self, objeto, x, y):
        self.dicMapa[y, x] = objeto.get_uid()

    def del_object(self, objeto):
        x, y = objeto.get_coor()
        self.clean_coor(x, y)

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

        if not pos:
            raise exceptions.TeamBasePositionNotFound

        x, y = pos
        self.set_object(jugador, x, y)
        jugador.mover(x, y)
        return jugador

    def clean_coor(self, x, y):
        self.dicMapa[y, x] = 0

    def pos_is_blocked(self, x, y):
        return self.dicMapa[y, x] >= 1

    def get_empty_place(self, x, y):
        cuadrante = [[-1, -1], [0, -1], [1, -1],
                     [-1,  0],          [1,  0],
                     [-1,  1], [0,  1], [1,  1]]

        for pos in cuadrante:
            nx = x + pos[0]
            ny = y + pos[1]
            if not self.pos_is_blocked(nx, ny):
                return nx, ny
        # todo ocupado
        return None

    def gen_mapa_char(self):
        # TODO: change this -> just send the 2d array
        long_fila = None
        filas = ""
        for y in self.compacto:
            # la longitud de fila se calcula 1 sola vez, ya que el mapa "debe" ser rectangular
            if not long_fila:
                # al ser char cada longitud de fila: tiene que ser menor a 255
                long_fila = chr(len(y))
            # pasamos a char
            fila_char = ""
            for i in range(0, len(y), 8):
                fila_char += chr(int(y[i:i+8], 2))
            filas += fila_char
        self.mapaChar = long_fila + filas

    def move_player(self, jugador, x, y):
        antx, anty = jugador.get_coor()
        jugador.mover(x, y)
        self.clean_coor(antx, anty)
        self.set_object(jugador, x, y)

    def clean_map(self):
        for (y, x) in self.dicMapa:
            if self.dicMapa[y, x] != 1:
                self.dicMapa[y, x] = 0
