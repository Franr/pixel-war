import pygame
from constantes import SQM, C_BLOQUE, C_FONDO


block_colors = {
    'b': C_BLOQUE,
    'n': C_FONDO
}


class MapLogic(object):

    def __init__(self, array_map):
        self.dicMapa = {}
        # calculating the map dimensions
        self.y = len(array_map)
        self.x = len(array_map[0])
        # generate the map structure
        self._pre_generate_surf()
        for i in range(len(array_map)):
            for e in range(len(array_map[i])):
                obj_id = int(array_map[i][e])
                bloq = 'b' if obj_id else 'n'
                self.dicMapa[i, e] = (bloq, obj_id)
                self._render_sqm(e, i, bloq)
        self._post_generate_surf()

    def _pre_generate_surf(self):
        pass

    def _render_sqm(self, x, y, bloq_type):
        pass

    def _post_generate_surf(self):
        pass

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


class Mapa(MapLogic):

    def _pre_generate_surf(self):
        self.surf = pygame.Surface((self.x * SQM, self.y * SQM))

    def _render_sqm(self, x, y, bloq_type):
        rect = pygame.Rect(x*SQM, y*SQM, 20, 20)
        pygame.draw.rect(self.surf, block_colors[bloq_type], rect)

    def _post_generate_surf(self):
        self.surf = self.surf.convert()
