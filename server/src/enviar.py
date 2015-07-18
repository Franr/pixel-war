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

from handlers import HandlerCriaturas

DEBUG = False

class Enviar:

    FIN_PAQUETE = '||'
    SEPARADOR = '|'
    IT1NIVEL = 'i-'
    ITCOMPLETA = 't-'

    def __init__(self, socket_cliente, accion, datos):        
        ''' Envia un paquete a un cliente especifico '''        
        # generamos el paquete
        self.genPaquete(accion, datos)        
        # lo enviamos
        try:
            socket_cliente.send(self.paquete)
            if DEBUG: print 'Paquete enviado: ', self.paquete
        except:
            print "Error al enviar el mensaje:", self.paquete
        
    def genPaquete(self, accion, datos):
        ## Este metodo es un asco!
        ## modificar mas adelante
        ## 04/04/10
        paquete = accion
        for p in datos:
            # Algunos datos son arreglos iterables, por lo que hay que separarlos tambien
            # Para saber en cuales hay que iterar se antepone un 'i-' al principio de la lista
            try:
                # Si es iterable, y empieza con la respectiva senia, entonces hay que destriparlo :-P
                ## ITERACION DE 1 NIVEL (para no iterar sobre los strings)
                if p[0] == Enviar.IT1NIVEL:
                    p = p[1:]
                    for i in p:
                        paquete = paquete + Enviar.SEPARADOR + str(i)
                ## ITERACION COMPLETA
                elif p[0] == Enviar.ITCOMPLETA:
                    p = p[1:]
                    p = self.iterar(p)
                    for i in p:
                        paquete = paquete + Enviar.SEPARADOR + str(i)
                else:
                    d = Enviar.SEPARADOR + str(p)
                    paquete += d
            except:
                d = Enviar.SEPARADOR + str(p)
                paquete += d                
        paquete += Enviar.FIN_PAQUETE
        self.paquete = paquete
    
    def iterar(self, arreglo):
        ''' Genera un arreglo con todos los elementos de un arreglo de N arreglos '''
        dev = []
        try:
            for i in arreglo:
                dev.extend(iterar(i))
        except:
            return arreglo
        return dev

      
class EnviarListos:

    def __init__(self, jugadores, accion, datos):
        sockets = []
        for j in jugadores.values():  # jugadores es un diccionario
            if j.listo:
                sockets.append(j.socket)
        EnviarVarios(sockets, accion, datos)


class EnviarTodos:
    
    def __init__(self, accion, datos):
        sockets = [j.socket for j in HandlerCriaturas().getJugadores().values()]
        EnviarVarios(sockets, accion, datos)


class EnviarVarios:

    def __init__(self, sockets, accion, datos, sock_excepcion=None):
        for s in sockets:
            if s != sock_excepcion:
                Enviar(s, accion, datos)               