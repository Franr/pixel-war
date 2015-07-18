import threading, time
from entidades import Jugador, Bala

DEBUG = False


class Singleton(type):
 
    def __init__(cls, name, bases, dct):
        cls.__instance = None
        type.__init__(cls, name, bases, dct)
 
    def __call__(cls, *args, **kw):
        if cls.__instance is None:
            cls.__instance = type.__call__(cls, *args,**kw)
        return cls.__instance


class HandlerId:

    def __init__(self):
        # el id 0 se reserva para los espacios vacios
        # el id 1 se reserva para los bloques
        self.id = 2
        
    def getSiguienteId(self):
        self.id += 1
        return self.id


class HandlerCriaturas:

    __metaclass__ = Singleton

    VIDA_MAX = 100
    mapa = None
    ronda = None

    def __init__(self):
        self.jugadores = {}
        self.handler_id = HandlerId()

    def crearJugador(self, x, y, equipo):
        id = self.handler_id.getSiguienteId()
        # instanciamos
        j = Jugador(id, x, y, self.VIDA_MAX, self.VIDA_MAX, equipo, self)
        self.jugadores[id] = j
        # ubicamos el jugador en el mapa
        self.mapa.setObjeto(j, x, y)
        return j

    def desconectarJugador(self, id):
        # se llama cuando se desconecta un jugador
        criat = self.delCriaturaById(id)
        if criat:
            self.mapa.delObjeto(criat)
            if DEBUG: print("criatura eliminada:", id)
            
    def eliminarJugador(self, id):
        # se llama cuando se muere un jugador
        jug = self.getCriaturaById(id)
        if jug:
            self.mapa.delObjeto(jug)
            if DEBUG: print("jugador eliminado:", id)
        
    def delCriaturaById(self, id):
        if self.jugadores.has_key(id):
            return self.jugadores.pop(id)
        else:
            return None
            
    def getCriaturaById(self, id):
        if self.jugadores.has_key(id):
            return self.jugadores[id]
        else:
            return None

    def getJugadores(self):
        return self.jugadores
        
    def getMapa(self):
        return self.mapa
        
    def comenzarRonda(self):
        if len(self.jugadores) > 1:
            if not self.ronda.comenzada:
                if not self.ronda.restarting:
                    self.ronda.comenzar()
                
    def restartJugadores(self):
        self.mapa.limpiarTodo()
        nuevas_pos = []
        for j in self.jugadores.values():
            j.revivir()
            nuevas_pos.extend(self.mapa.posicionar(j))
        return nuevas_pos
        
    def restartRonda(self):
        self.ronda.restart()


class HandlerBala(threading.Thread):

    def __init__(self, jug, dir, prot):
        threading.Thread.__init__(self)
        self.bala = Bala(jug.id, jug.x, jug.y, dir, jug.getEquipo())
        self.prot = prot
        self.hcriat = HandlerCriaturas()
        self.mapa = self.hcriat.getMapa()
        self.jug = jug
        self.jug.bloquearDisp()
        self.start()
    
    def run(self):
        res = True
        while res:
            res = self.update()
            time.sleep(self.bala.DELAY)
            
    def update(self):
        # proximo movimiento
        x = self.bala.x + self.bala.dx
        y = self.bala.y + self.bala.dy
        # recuperamos el id de lo que haya en la proxima posicion
        id = self.mapa.getIdByPos(x, y)
        # choco contra algo?
        if id not in (0, self.bala.getId()):
            # contra un bloque?
            if id == 1:
                return False
            # contra una criatura?
            else:
                c = self.hcriat.getCriaturaById(id)
                if c:
                    # criatura del mismo equipo?
                    if self.bala.esEquipo(c.getEquipo()):
                        self.bala.mover()
                        return True
                    # criatura enemiga
                    else:
                        # atacamos
                        if c.estaVivo():
                            if c.hit(self.bala.DMG):
                                MurioJugador(c, self.prot)
                            else:
                                self.prot.enviarHit(c, self.bala.DMG)
                        return False
                else:
                    # error
                    return False
        # no choco o choco contra su propio duenio
        else:
            # seguimos
            self.bala.mover()
            return True


class MurioJugador:

    def __init__(self, jugador, prot):
        hc = HandlerCriaturas()        
        prot.enviarEliminarCriatura(jugador.getId())
        hc.ronda.murio(jugador.getEquipo())
