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

import pygame
from constantes import *

class Mapa:
    
    def __init__(self, secuencia):
        self.dicMapa = {}
        self.parseMapa(secuencia)
        
    def parseMapa(self, sec):
        # calculamos las dimensiones del mapa
        # primer caracter -> longitud de columnas
        self.x = ord(sec[0])
        sec = sec[1:]
        # longitud de fila = todas las celdas divido longitud de columna
        # cada char contiene 8 ids
        self.y = len(sec) * 8 / self.x        
        # paramos los chars a enteros, y de enteros a binarios
        #str(ord("\x01")).rjust(8, "0")
        sec = [str(bin(ord(i))[2:]).rjust(8, "0") for i in sec]
        #print sec
        #return
        filas = []
        i = 0
        while i < len(sec):
            fila = ""
            while len(fila) < self.x:
                fila += sec[i]
                i += 1
            filas.append(fila)
                   
        # generamos la superficie que vamos a usar para dibujar
        self.surf = pygame.Surface((self.x * SQM, self.y * SQM))
        self.surf.fill((255, 255, 255))
        for i in range(len(filas)):
            for e in range(len(filas[i])):
                id = int(filas[i][e])
                if id:
                    bloq = "b"
                    color = C_BLOQUE
                else:
                    bloq = "n"
                    color = C_FONDO
                self.dicMapa[i, e] = (bloq, id)
                rect = pygame.Rect(e * SQM, i * SQM, 20, 20)
                pygame.draw.rect(self.surf, color, rect)
        self.surf = self.surf.convert()
        
    def calcDim(self, sec):
        return len(sec[0].split(',')), len(sec)        
        
    def desborda(self, x, y):
        ''' devuelve True si la posicion (x, y) desborda del mapa '''
        return ((x < 0) or (y < 0)) or ((x >= self.x) or (y >= self.y))
        
    def esPosBloqueante(self, x, y):
        return self.dicMapa[y, x][0] == "b" 
            
    def moverCriatura(self, criatura, x, y):
        x_ant, y_ant = criatura.getCoor()
        self.setCriatura(criatura, x, y)
        self.limpiarPos(x_ant, y_ant)
            
    def setCriatura(self, criatura, x, y):
        self.dicMapa[y, x] = ("b", criatura)
    
    def limpiarPos(self, x, y):
        self.dicMapa[y, x] = ("n", 0)
        
    def getCriatura(self, x, y):
        if self.dicMapa[y, x][0] == "n":
            return None
        elif self.dicMapa[y, x][0] == "b":
            if isinstance(self.dicMapa[y, x][1], int):
                return None
            else:
                return self.dicMapa[y, x][1]