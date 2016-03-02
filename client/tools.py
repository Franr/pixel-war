import os
import pygame


class Archivo(object):

    """ Lee un archivo y lo almacena como una cadena """

    def __init__(self, nombre):    
        # Nos posicionamos en la carpeta correspondiente
        ruta = os.path.join("src", nombre)
        # Contenedor
        self.buffer = []
        # Abrimos el archivo
        archivo = open(ruta, 'Ur')
        # Leemos y almacenamos
        while True:
            linea = archivo.readline()
            if not linea:
                break
            if not linea.startswith("#"):
                self.buffer.append(linea.rstrip('\n'))
                
        print 'Archivo:', nombre, 'cargado con exito.'


class ArchivoEditable(object):

    def __init__(self, carpeta, nombre):
        # nos posicionamos en la carpeta correspondiente
        ruta = os.path.join(carpeta, nombre)
        # Abrimos el archivo
        self.archivo = open(ruta, 'w')
        
    def escribir(self, string):
        self.archivo.write(string)
        
    def cerrar(self):
        self.archivo.close()


class Fuente(object):

    def __init__(self, size):
        pygame.font.init()
        self.size = size
        self.nombre = "cubicfive10.ttf"  # TODO: move it to constants/config file
        ruta = os.path.join("client", self.nombre)
        self.fuente = pygame.font.Font(ruta, self.size)

    def render(self, text, color):
        """Return a surface with the given text and color

        :type text: str
        :param text: The text to be rendered

        :type color: tuple
        :param color: The color of the text

        :rtype: Surface
        :return: Returns a Surface with the text in the selected color
        """
        return self.fuente.render(text, False, color)
