import os


class Archivo:

    """ Lee un archivo y lo almacena como una cadena """

    def __init__(self, folder, name):

        # Nos posicionamos en la carpeta correspondiente
        path = os.path.join(folder, name)
        # Contenedor
        self.buffer = []
        # Abrimos el archivo
        archivo = open(path, 'r')
        # Leemos y almacenamos
        while True:
            linea = archivo.readline()
            if not linea:
                break
            if not linea.startswith("#"):
                self.buffer.append(linea.rstrip('\n'))
