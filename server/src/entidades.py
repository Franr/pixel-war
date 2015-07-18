#
#    Pixel War (Server) - Server de Juego Multiplayer Online
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

from bloqueos import BloqueoMov, BloqueoDisp


class Objeto:
    ''' Clase base para todos los objetos (visibles) del juego '''

    def __init__(self, id, x, y):
        self.x = x
        self.y = y
        self.id = id

    def getCoor(self):
        return (self.x, self.y)

    def setCoor(self, x, y):    
        self.x = x
        self.y = y
        
    def esId(self, id):
        return self.id == id
        
    def getId(self):
        return self.id       


class Criatura(Objeto):
    ''' Clase base para todas las criaturas (tanto para jugadores como monstruos '''    
    
    def __init__(self, id, x, y, vida, vida_max, hcriat):
        Objeto.__init__(self, id, x, y)
        self.vida = vida
        self.vida_max = vida_max
        self.vivo = True
        self.envenenado = False
        self.hcriat = hcriat
        
    def mover(self, x, y):
        self.setCoor(x, y)
        
    def estaVivo(self):
        return self.vivo
        
    def getEquipo(self):
        return self.equipo
        
    def esEquipo(self, equipo):
        return self.equipo == equipo

    def hit(self, danio):
        self.vida -= danio
        if self.vida <= 0:
            self.morir()
            return True
        return False
            
    def morir(self):
        if self.vivo:
            self.vivo = False
            self.morirAccion()
            
    def morirAccion(self):
        self.hcriat.eliminarCriatura(self.getId())


class Jugador(Criatura):
    ''' Clase para todos los jugadores del juego '''
    
    def __init__(self, id, x, y, vida, vida_max, equipo, hcriat):
        Criatura.__init__(self, id, x, y, vida, vida_max, hcriat)
        self.equipo = equipo
        self.bloqM = BloqueoMov()
        self.bloqD = BloqueoDisp()
        # un jugador esta listo una vez asignados todos sus datos
        self.listo = False
        
    def setListo(self):
        self.listo = True

    def getDatos(self):
        # devuelve los datos necesarios para el paquete de creacion de jugador
        return [self.getId(), self.equipo, self.x, self.y, self.vida, self.vida_max]
    
    def mover(self, x, y):
        Criatura.mover(self, x, y)
        self.bloquearMov()
    
    def bloquearMov(self):
        self.bloqM = BloqueoMov()
    
    def bloquearDisp(self):
        self.bloqD = BloqueoDisp()
        
    def estaBloqueadoMov(self):
        return self.bloqM.bloq
        
    def estaBloqueadoDisp(self):
        return self.bloqD.bloq
        
    def morirAccion(self):
        self.hcriat.eliminarJugador(self.getId())
        
    def revivir(self):
        self.vivo = True
        self.vida = self.vida_max
        
        
class Bala(Objeto):

    DELAY = 0.05   
    DMG = 5#100

    def __init__(self, id, x, y, dir, equipo):
        Objeto.__init__(self, id, x, y)
        self.dir = dir
        self.equipo = equipo
        self.dx = 0
        self.dy = 0
        for d in dir:
            self.calcularDesplazamiento(d)
        
    def esEquipo(self, equipo):
        return self.equipo == equipo
        
    def calcularDesplazamiento(self, dir):
        if dir == 'n':
            self.dy = -1
        elif dir == 's':
            self.dy = 1
        elif dir == 'e':
            self.dx = 1
        elif dir == 'o':
            self.dx = -1
        
    def mover(self):    
        self.setCoor(self.x + self.dx, self.y + self.dy)