from handlers import HandlerCriaturas
from protocol import Protocolo


class SingletonRonda(type):
 
    def __init__(cls, name, bases, dct):
        cls.__instance = None
        type.__init__(cls, name, bases, dct)
 
    def __call__(cls):
        if cls.__instance is None:
            cls.__instance = type.__call__(cls)
        return cls.__instance


class Ronda(object):

    # Esta clase es SINGLETON
    __metaclass__ = SingletonRonda

    def __init__(self):
        self.comenzada = False
        self.restarting = False
        self.total_azul = 0
        self.total_rojo = 0
        self.ronda = 0

    def jugando(self):
        return self.comenzada and not self.restarting

    def _descontar(self, equipo):
        if equipo == "r":
            self.rojos -= 1
        else:
            self.azules -= 1
        self._check()

    def _check(self):
        if self.rojos <= 0:
            self._ganoAzul()
            self.nuevaRonda()
        elif self.azules <= 0:
            self._ganoRojo()
            self.nuevaRonda()

    def _ganoAzul(self):
        self.total_azul += 1
        Protocolo.enviarNuevaRonda()

    def _ganoRojo(self):
        self.total_rojo += 1
        Protocolo.enviarNuevaRonda()

    def nuevaRonda(self):
        if not self.restarting:
            #tc = threading.Thread(target=self.comenzar)
            #tc.start()
            self.comenzar()

    def get(self):
        return self.total_azul, self.total_rojo, self.ronda

    def restart(self):
        self.total_azul = 0
        self.total_rojo = 0
        self.ronda = 0
        self.nuevaRonda()

    def comenzar(self):
        # contamos todos los jugadores que hay en cada equipo
        self.rojos = 0
        self.azules = 0
        jugs = HandlerCriaturas().get_players().values()
        for j in jugs:
            if j.es_equipo("r"):
                self.rojos += 1
            else:
                self.azules += 1
        # la partida empieza solo si hay jugadores en los 2 equipos
        if self.rojos and self.azules:
            # una ronda tarda 3 segundos para comenzar
            print "comenzando nueva ronda en 3 segundos..."
            # acomodamos los jugadores
            np = HandlerCriaturas().restart_players()
            #self.restarting = True
            #time.sleep(3)
            #self.restarting = False
            Protocolo.enviarNuevasPos(np)
            # arrancamos
            self.comenzada = True
            self.ronda += 1
            print "Ronda nro:", self.ronda
            Protocolo.enviarNuevaRonda()
    
    def salio(self, equipo):
        if self.jugando():
            self._descontar(equipo)
        
    def murio(self, equipo):
        if self.jugando():
            self._descontar(equipo)