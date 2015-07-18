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

import threading, time

class Bloqueo(threading.Thread):

    def __init__(self, tiempo):
        threading.Thread.__init__(self)
        self.tiempo = tiempo
        self.bloq = True
        
    def run(self):
        time.sleep(self.tiempo)
        self.bloq = False


class BloqueoMov(Bloqueo):
    
    def __init__(self):
        Bloqueo.__init__(self, 0.15)
        self.start()
        
class BloqueoDisp(Bloqueo):
    
    def __init__(self):
        Bloqueo.__init__(self, 0.10)
        self.start()