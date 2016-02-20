import pygame
from constantes import SQM, C_BLOQUE, C_FONDO


class Mapa(object):

    def __init__(self, array_map):
        self.dicMapa = {}
        # calculamos las dimensiones del mapa
        self.y = len(array_map)
        self.x = len(array_map[0])
        # generamos la superficie que vamos a usar para dibujar
        self.surf = pygame.Surface((self.x * SQM, self.y * SQM))
        self.surf.fill((255, 255, 255))
        for i in range(len(array_map)):
            for e in range(len(array_map[i])):
                obj_id = int(array_map[i][e])
                if obj_id:
                    bloq = "b"
                    color = C_BLOQUE
                else:
                    bloq = "n"
                    color = C_FONDO
                self.dicMapa[i, e] = (bloq, obj_id)
                rect = pygame.Rect(e * SQM, i * SQM, 20, 20)
                pygame.draw.rect(self.surf, color, rect)
        self.surf = self.surf.convert()

    def desborda(self, x, y):
        """ devuelve True si la posicion (x, y) desborda del mapa """
        return ((x < 0) or (y < 0)) or ((x >= self.x) or (y >= self.y))

    def is_blocking_position(self, x, y):
        return self.dicMapa[y, x][0] == "b"

    def move_creature(self, criatura, x, y):
        x_ant, y_ant = criatura.get_coor()
        self.set_creature(criatura, x, y)
        self.clean_position(x_ant, y_ant)

    def set_creature(self, criatura, x, y):
        self.dicMapa[y, x] = ("b", criatura)

    def clean_position(self, x, y):
        self.dicMapa[y, x] = ("n", 0)

    def get_creature(self, x, y):
        if self.dicMapa[y, x][0] == "n":
            return None
        elif self.dicMapa[y, x][0] == "b":
            if isinstance(self.dicMapa[y, x][1], int):
                return None
            else:
                return self.dicMapa[y, x][1]
