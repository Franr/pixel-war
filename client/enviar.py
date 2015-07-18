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

LOGS = False

class Enviar:

    SOCKET = None
    SEPARADOR = '|'
    
    def __init__(self, accion, datos):    
        self.genPaquete(accion, datos)
        try:
            self.SOCKET.send(self.paquete)
        except UnicodeEncodeError:
            if LOGS: print "Error: Paquete con caracteres no permitidos"
            return
        if LOGS: print 'Paquete enviado: ', self.paquete
        
    def genPaquete(self, accion, datos):    
        paquete = accion
        for p in datos:
            add = self.SEPARADOR + p
            paquete += add
        self.paquete = paquete