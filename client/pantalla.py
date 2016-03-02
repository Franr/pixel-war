import pygame
import pygame.gfxdraw
from constantes import FPS_MAX, C_AMARILLO, C_FONDO, C_JUG_A, C_JUG_R, CONST_CENTRAR, SQM, P_X, P_Y
from tools import Fuente


class Pantalla(object):

    def __init__(self, game):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.dibujar = Drawer(game)
        self.activado = False

    def activar(self):
        self.activado = True

    def update(self):
        self.draw_game()
        self.refresh()

    def draw_game(self):
        if self.activado:
            self.dibujar.draw_game()

    def refresh(self):
        # FPS
        pygame.display.set_caption("Pixel War - FPS: %d" % self.clock.get_fps())
        # mostramos todo
        pygame.event.pump()
        pygame.display.flip()
        self.clock.tick(FPS_MAX)

    def set_principal(self, jugador):
        self.dibujar.set_principal(jugador)


class Drawer(object):

    """ Clase que se encarga de dibujar el juego """

    def __init__(self, game, ):
        self.game = game
        self.pantalla = pygame.display.set_mode((P_X, P_Y), pygame.DOUBLEBUF)
        self.fuente = Fuente(30)
        self.you = None
        self.mapa = None

    def set_principal(self, player):
        self.you = player

    def set_map(self, mapa):
        self.mapa = mapa

    def draw_game(self):
        # dibujamos el mapa
        self.draw_map()
        # dibujamos el score
        self.draw_score()
        # dibujamos los jugadores
        for j in self.game.get_players():
            self.draw_sprite(j)
        # dibujamos las balas
        for b in self.game.get_bullets():
            self.draw_bullets(b)
        # dibujamos los indicadores

    def draw_map(self):
        self.pantalla.fill(C_FONDO)
        self.pantalla.blit(self.mapa.surf, (
            (CONST_CENTRAR - self.you.x) * SQM, (CONST_CENTRAR - self.you.y) * SQM))

    def draw_score(self):
        blue, red = self.game.get_score()
        srf_azul = self.fuente.render(str(blue) + '|', C_JUG_A)
        srf_rojo = self.fuente.render(str(red) + '|', C_JUG_R)
        self.pantalla.blit(srf_azul, (P_X - srf_azul.get_width(), 0))
        self.pantalla.blit(srf_rojo, (P_X - srf_rojo.get_width(), 30))

    def draw_sprite(self, criatura):
        if not criatura.esta_vivo():
            return

        # calculamos las coordenadas
        x, y = self.coor_objeto_centradas(criatura)
        # color de equipo
        if criatura.get_equipo() == 1:
            color = list(C_JUG_A)
        else:
            color = list(C_JUG_R)
        # dibujamos los rects
        color_t = color + [criatura.get_vida() * 255 / 100]
        rect = pygame.Rect(x, y, SQM, SQM)
        pygame.gfxdraw.box(self.pantalla, rect, color_t)
        pygame.gfxdraw.rectangle(self.pantalla, rect, color)

    def draw_bullets(self, bala):
        x, y = self.coor_objeto_centradas(bala)
        rect = pygame.Rect(x, y, SQM, SQM)
        pygame.draw.rect(self.pantalla, C_AMARILLO, rect)

    def coor_objeto_centradas(self, criat):
        x = (CONST_CENTRAR + criat.x - self.you.x) * SQM
        y = (CONST_CENTRAR + criat.y - self.you.y) * SQM
        return x, y
