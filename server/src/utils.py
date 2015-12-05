import os


class Archivo(object):

    """ Lee un archivo y lo almacena como una cadena """

    def __init__(self, carpeta, nombre, metodo):

        # Nos posicionamos en la carpeta correspondiente
        ruta = os.path.join(carpeta, nombre)
        # Contenedor
        self.buffer = []
        # Abrimos el archivo
        archivo = open(ruta, 'U' + metodo)
        # Leemos y almacenamos
        while True:
            linea = archivo.readline()
            if not linea:
                break
            if not linea.startswith("#"):
                self.buffer.append(linea.rstrip('\n'))
