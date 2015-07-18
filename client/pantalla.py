import pygame
import pygame.gfxdraw
from constantes import *
from tools import Fuente


class Pantalla:

    def __init__(self, hcriat, balas, srf=None):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.dibujar = Dibujar(hcriat, balas, srf)
        self.hcriat = hcriat
        self.activado = False
        
    def activar(self):
        self.activado = True

    def update(self):
        self.dibujarJuego()
        self.refresh()
        
    def salir(self):
        pygame.quit()
        
    def dibujarJuego(self):
        if self.activado:
            self.dibujar.dibJuego()

    def refresh(self):
        # FPS
        pygame.display.set_caption("Pixel War - FPS: %d" % self.clock.get_fps())
        # mostramos todo
        pygame.event.pump()
        pygame.display.flip()
        self.clock.tick(FPS_MAX)

    def setPrincipal(self, jugador):
        self.dibujar.setPrincipal(jugador)


class Dibujar:

    ''' Clase que se encarga de dibujar el juego '''   

    def __init__(self, hcriat, balas, srf=None):
        self.hcriat = hcriat
        self.balas = balas
        if not srf:
            self.pantalla = pygame.display.set_mode((P_X, P_Y), pygame.DOUBLEBUF)
        else:
            self.pantalla = srf
        self.fuente = Fuente(30)

    def setPrincipal(self, jugador):
        self.principal = jugador

    def setMapa(self, mapa):
        self.mapa = mapa

    def dibJuego(self):
        # dibujamos el mapa
        self.dibMapa()
        # dibujamos el score
        self.dibScore()
        # dibujamos los jugadores
        for j in self.hcriat.getJugadores():
            self.dibSprite(j)
        # dibujamos las balas
        for b in self.balas.getBalas():
            self.dibBalas(b)
        # dibujamos los indicadores

    def dibMapa(self):
        self.pantalla.fill(C_FONDO)
        self.pantalla.blit(self.mapa.surf, ((CONST_CENTRAR - self.principal.x) * SQM, (CONST_CENTRAR - self.principal.y)* SQM))

    def dibScore(self):
        srf_azul = self.fuente.render(str(self.hcriat.azul) + '|', C_JUG_A)
        srf_rojo = self.fuente.render(str(self.hcriat.rojo) + '|', C_JUG_R)
        srf_rond = self.fuente.render(str(self.hcriat.ronda) + '|', C_NEGRO)
        self.pantalla.blit(srf_azul, (P_X - srf_azul.get_width(), 0))
        self.pantalla.blit(srf_rojo, (P_X - srf_rojo.get_width(), 30))
        self.pantalla.blit(srf_rond, (P_X - srf_rond.get_width(), 60))

    def dibSprite(self, criatura):
        if criatura.estaVivo():
            # calculamos las coordenadas
            x, y = self.coorObjetoCentradas(criatura)
            # color de equipo
            if criatura.getEquipo() == "r":
                color = list(C_JUG_R)
            else:
                color = list(C_JUG_A)
            # dibujamos los rects
            color_t = color + [criatura.vida.get() * 255 / 100]
            rect = pygame.Rect(x, y, SQM, SQM)
            pygame.gfxdraw.box(self.pantalla, rect, color_t)
            pygame.gfxdraw.rectangle(self.pantalla, rect, color)
            #pygame.draw.rect(self.pantalla, color, rect)

    def dibBalas(self, bala):
        x, y = self.coorObjetoCentradas(bala)
        rect = pygame.Rect(x, y, SQM, SQM)
        pygame.draw.rect(self.pantalla, C_AMARILLO, rect)

    def coorObjetoCentradas(self, criat):
        x = (CONST_CENTRAR + criat.x - self.principal.x) * SQM
        y = (CONST_CENTRAR + criat.y - self.principal.y) * SQM
        return x, y
