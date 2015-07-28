import os
from utils import Archivo


class Mapa(object):

    ## Dividir en 2 clases:
    ## el mapa y el handler del mapa
    
    ## atencion:
    ## internamente la clase maneja las coordenadas primero a "Y" y despues a "X"
    ## por la manera en que se splitea el mapa desde el archivo.
    ## pero las llamadas a los metodos desde afuera se hace igual que siempre: x, y.
    
    ## El mapa solo contiene ids en sus arrays:
    ## = 0  libre
    ## = 1  bloque
    ## > 1  jugador    

    def __init__(self, nombre):
        self.nombre = nombre
        self.mapaChar = None
        # cargamos los mapas numericos
        maps_folder = os.path.dirname(__file__) + '/../maps'
        sec = self.parse(Archivo(maps_folder, nombre + ".pwm", "r").buffer)
        if sec:
            self.genMapaNumerico(sec)
            self.genMapaChar()

    def parse(self, sec):
        # Dividimos c/linea por las comas
        for i in range(len(sec)):
            sec[i] = sec[i].split(',')
            if len(sec[i]) % 8:
                print "Error: Longitud de fila no divisible por 8."
                return None
                
        # calculamos las medidas del mapa:
        self.dy = len(sec)
        self.dx = len(sec[0])
        return sec

    def genMapaNumerico(self, mapa):
        self.dicMapa = {}
        self.compacto = []
        for y in range(len(mapa)):
            fila_compacta = ""
            for x in range(len(mapa[y])):
                id = int(mapa[y][x])
                if id == 2:
                    # respawn rojo
                    self.setRojo(x, y)
                    id = 0
                elif id == 3:
                    # respawn azul
                    self.setAzul(x, y)
                    id = 0
                self.dicMapa[y, x] = id
                fila_compacta += str(id)
            # el compacto se usa para enviar el mapa en formato binario
            self.compacto.append(fila_compacta)

    def getIdByPos(self, x, y):
        return self.dicMapa[y, x]

    def getObjeto(self, x, y):
        return self.dicMapa[y, x]

    def setObjeto(self, objeto, x, y):
        self.dicMapa[y, x] = objeto.get_uid()

    def delObjeto(self, objeto):
        x, y = objeto.get_coor()
        self.limpiarCoor(x, y)

    def setRojo(self, x, y):
        self.x_rojo = x
        self.y_rojo = y

    def setAzul(self, x, y):
        self.x_azul = x
        self.y_azul = y

    def getRojo(self):
        if self.posBloqueada(self.x_rojo, self.y_rojo):
            return self.getPosVaciasAlrededorPos(self.x_rojo, self.y_rojo)
        else:
            return self.x_rojo, self.y_rojo

    def getAzul(self):
        if self.posBloqueada(self.x_azul, self.y_azul):
            return self.getPosVaciasAlrededorPos(self.x_azul, self.y_azul)
        else:
            return self.x_azul, self.y_azul

    def posicionar(self, jugador):
        if jugador.get_equipo() == "a":
            pos = self.getAzul()
        else:
            pos = self.getRojo()
            
        if pos:
            x, y = pos
            self.setObjeto(jugador, x, y)
            jugador.mover(x, y)
            return jugador.get_uid(), x, y
        else:
            print "error al ubicar", jugador.get_uid()

    def limpiarCoor(self, x, y):
        self.dicMapa[y, x] = 0

    def posBloqueada(self, x, y):
        return self.dicMapa[y, x] >= 1

    def getDim(self):
        # devuelve las dimensiones del mapa
        return self.dx, self.dy

    def getIdCriatura(self, x, y):
        # devuelve el id de la criatura en la posicion x, y
        # si no hay criatura devuelve None
        
        # comprobamos que las coordenadas no desborden
        if (x < 0) or (x > self.dx - 1) or (y < 0) or (y > self.dy - 1):
            return None
            
        if self.dicMapa[y, x] > 1:
            return self.dicMapa[y, x]
        else:
            return None

    def getPosVaciasAlrededorPos(self, x, y):
        cuadrante = [[-1, -1], [0, -1], [1, -1],
                     [-1,  0],          [1,  0],
                     [-1,  1], [0,  1], [1,  1]]
                     
        for pos in cuadrante:
            nx = x + pos[0]
            ny = y + pos[1]
            if not self.posBloqueada(nx, ny):
                return nx, ny
        # todo ocupado
        return None

    def getIdCriaturasAlrededorCriatura(self, criatura):
        cuadrante = [[-1, -1], [0, -1], [1, -1],
                     [-1,  0],          [1,  0],
                     [-1,  1], [0,  1], [1,  1]]
                     
        x, y = criatura.get_coor()
        ids = []
        for pos in cuadrante:
            id = self.getIdCriatura(x + pos[0], y + pos[1])
            # hay criatura?
            if id:
                ids.append(id)
        return ids

    def getMapaChar(self):
        return self.mapaChar

    def genMapaChar(self):
        long_fila = None
        filas = ""
        for y in self.compacto:
            # la longitud de fila se calcula 1 sola vez, ya que el mapa "debe" ser rectangular
            if not long_fila:
                # al ser char cada longitud de fila: tiene que ser menor a 255
                long_fila = chr(len(y))
            # pasamos a char
            fila_char = ""
            for i in range(0, len(y), 8):
                fila_char += chr(int(y[i:i+8], 2))
            filas += fila_char
        self.mapaChar = long_fila + filas

    def moverJugador(self, jugador, x, y):
        antx, anty = jugador.get_coor()
        jugador.mover(x, y)
        self.limpiarCoor(antx, anty)
        self.setObjeto(jugador, x, y)

    def limpiarTodo(self):
        for (y, x) in self.dicMapa:
            if self.dicMapa[y, x] != 1:
                self.dicMapa[y, x] = 0
