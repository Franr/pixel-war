from twisted.internet import reactor
from twisted.internet.task import LoopingCall

from client.map_logic import MapLogic
from ia.ia import avoid_shoot, shoot_enemy, move
from generic_client import GenericClient


class Bot(GenericClient):

    STANDALONE = False
    DESIRED_FPS = 30.0  # 30 frames per second

    def run_loop(self):
        self.loop = LoopingCall(self.update)
        self.loop.start(1.0 / self.DESIRED_FPS)
        if self.STANDALONE:
            reactor.run()

    def load_io_handlers(self):
        pass

    def update(self):
        avoid_shoot(self.principal, self.balas.bullets, self.conexion)
        shoot_enemy(self.principal, self.hcriat.get_enemies(), self.conexion)
        move(self.principal, self.conexion)

    def activate_io_handlers(self):
        pass

    def set_principal(self, player):
        self.principal = player
        self.hcriat.my_team = player.equipo

    def get_uid(self):
        # TODO: this is just a hack, find a better approach
        if self.principal:
            return self.principal.uid
        return 1

    def create_map(self, sequence):
        return MapLogic(sequence)
