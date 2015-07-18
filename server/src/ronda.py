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

import threading
import time
from handlers import HandlerCriaturas
from protocol import Protocolo

class SingletonRonda(type):
 
    def __init__(cls, name, bases, dct):
        cls.__instance = None
        type.__init__(cls, name, bases, dct)
 
    def __call__(cls):#, *args, **kw):
        if cls.__instance is None:
            cls.__instance = type.__call__(cls)#, *args, **kw)
        return cls.__instance

        
class Ronda:

    # Esta clase es SINGLETON
    __metaclass__ = SingletonRonda
    
    def __init__(self):
        self.comenzada = False
        self.restarting = False
        self.total_azul = 0
        self.total_rojo = 0
        self.ronda = 0
        
    def jugando(self):
        return self.comenzada and not self.restarting
        
    def _descontar(self, equipo):
        if equipo == "r":
            self.rojos -= 1
        else:
            self.azules -= 1
        self._check()
        
    def _check(self):
        if self.rojos <= 0:
            self._ganoAzul()
            self.nuevaRonda()
        elif self.azules <= 0:
            self._ganoRojo()
            self.nuevaRonda()
            
    def _ganoAzul(self):
        self.total_azul += 1
        Protocolo.enviarNuevaRonda()
    
    def _ganoRojo(self):
        self.total_rojo += 1
        Protocolo.enviarNuevaRonda()
        
    def nuevaRonda(self):
        if not self.restarting:
            #tc = threading.Thread(target=self.comenzar)
            #tc.start()
            self.comenzar()
        
    def get(self):
        return self.total_azul, self.total_rojo, self.ronda
        
    def restart(self):
        self.total_azul = 0
        self.total_rojo = 0
        self.ronda = 0
        self.nuevaRonda()
        
    def comenzar(self):
        # contamos todos los jugadores que hay en cada equipo
        self.rojos = 0
        self.azules = 0
        jugs = HandlerCriaturas().getJugadores().values()
        for j in jugs:
            if j.esEquipo("r"):
                self.rojos += 1
            else:
                self.azules += 1
        # la partida empieza solo si hay jugadores en los 2 equipos
        if self.rojos and self.azules:
            # una ronda tarda 3 segundos para comenzar
            print "comenzando nueva ronda en 3 segundos..."
            # acomodamos los jugadores
            np = HandlerCriaturas().restartJugadores()
            #self.restarting = True
            #time.sleep(3)
            #self.restarting = False
            Protocolo.enviarNuevasPos(np)
            # arrancamos
            self.comenzada = True
            self.ronda += 1
            print "Ronda nro:", self.ronda
            Protocolo.enviarNuevaRonda()
    
    def salio(self, equipo):
        if self.jugando():
            self._descontar(equipo)
        
    def murio(self, equipo):
        if self.jugando():
            self._descontar(equipo)