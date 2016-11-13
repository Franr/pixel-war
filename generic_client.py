from client.bala import HandlerBalas
from client.conexion import Conexion
from client.criaturas import HandlerCreatures


class GenericClient(object):

    # set it to False in case you need to run the reactor elsewhere
    STANDALONE = True

    def __init__(self, host, equipo):
        self.on = True
        self.principal = None
        self.loop = None

        # handlers
        self.balas = HandlerBalas(self)
        self.hcriat = HandlerCreatures()
        self.load_io_handlers()
        self.conexion = Conexion(host, self, self.hcriat, equipo)
        self.run_loop()

    def run_loop(self):
        raise NotImplementedError()

    def load_io_handlers(self):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()

    def activate_io_handlers(self):
        raise NotImplementedError()

    def create_map(self, sequence):
        raise NotImplementedError()

    def set_principal(self, player):
        raise NotImplementedError()

    def add_bullet(self, bullet):
        self.balas.add_bullet(bullet)

    def get_players(self):
        return self.hcriat.get_players()

    def get_bullets(self):
        return self.balas.get_balas()

    def get_score(self):
        return self.hcriat.azul, self.hcriat.rojo
