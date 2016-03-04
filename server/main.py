from server.src.handlers import CreaturesHandler
from server.src.mapa import Mapa
from server.src.score import Score


class Server(object):

    def __init__(self):
        self.pw_map = Mapa("mapa")
        self.score = Score()
        self.hcriat = CreaturesHandler()
        self.hcriat.pw_map = self.pw_map
        self.hcriat.score = self.score
