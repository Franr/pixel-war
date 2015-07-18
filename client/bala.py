#
#    Pixel War (Cliente) - Cliente de Juego Multiplayer Online
#    Copyright (C) 2010 - Francisco Rivera
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from threading import Thread
import time
import pygame
from constantes import SQM
from criaturas import Objeto

class HandlerBalas(Thread):
    
    ''' Clase que almacena las balas que dibuja el cliente '''

    def __init__(self, juego):
        Thread.__init__(self)
        self.juego = juego
        self.balas = []
        self.start()
        
    def getBalas(self):
        return self.balas
        
    def agregarBala(self, bala):
        self.balas.append(bala)
        
    def run(self):
        while self.juego.on:
            for b in self.balas:
                if not b.seguir:
                    self.balas.remove(b)
            time.sleep(.1)                       


class Bala(Thread, Objeto):

    def __init__(self, id, x, y, dir, equipo, juego):
        Thread.__init__(self)
        Objeto.__init__(self, x, y)
        self.id = id
        self.dir = dir
        self.equipo = equipo
        self.juego = juego
        self.seguir = True
        self.mapa = juego.pantalla.dibujar.mapa
        self.setDelay()
        # go for it!
        self.start()
        
    def run(self):
        mx, my = self.calcDesplazamiento()
        while self.seguir and self.juego.on:
            self.x += mx
            self.y += my
            time.sleep(self.delay)
            self.balaUpdate()
        del(self)
    
    def setDelay(self):
        self.delay = 0.05
    
    def calcDesplazamiento(self):
        movx = 0
        movy = 0
        dist = 1
        if self.dir == 'e':
            movx = dist
        elif self.dir == 'se':
            movx = dist
            movy = dist
        elif self.dir == 's':
            movy = dist
        elif self.dir == 'so':
            movx = -dist
            movy = dist
        elif self.dir == 'o':
            movx = -dist
        elif self.dir == 'no':
            movx = -dist
            movy = -dist
        elif self.dir == 'n':
            movy = -dist
        elif self.dir == 'ne':
            movx = dist
            movy = -dist
        return movx, movy

    def balaUpdate(self):
        # cada bala revisa sus colisiones contra las criaturas que:
        #   estan vivas
        #   pertenecen al equipo contrario al de la bala
        self.update(self.x, self.y)
        # rects de los sprites
        # verificamos colisiones
        if self.mapa.esPosBloqueante(self.x, self.y):
            c = self.mapa.getCriatura(self.x, self.y)
            if c:
                # choca contra enemigo
                if not c.esEquipo(self.equipo):
                    self.seguir = False
            # choca contra bloque
            else:
                self.seguir = False
                