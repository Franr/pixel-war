import pygame

from constantes import SQM, C_BLOQUE, C_FONDO
from map_logic import MapLogic

block_colors = {
    'b': C_BLOQUE,
    'n': C_FONDO
}


class MapRender(MapLogic):

    def _pre_generate_surf(self):
        self.surf = pygame.Surface((self.x * SQM, self.y * SQM))

    def _render_sqm(self, x, y, sqm_type):
        rect = pygame.Rect(x*SQM, y*SQM, 20, 20)
        pygame.draw.rect(self.surf, block_colors[sqm_type], rect)

    def _post_generate_surf(self):
        self.surf = self.surf.convert()
