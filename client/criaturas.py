import pygame


class Objeto:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = self.getRect()
        
    def getCoor(self):
        return self.x, self.y
        
    def getRect(self):
        return pygame.Rect(self.x, self.y, 7, 7)
        
    def update(self, x, y):
        self.x = x
        self.y = y        
    
    def colisiona(self, rects):
        return self.rect.collidelist(rects) != -1


class HandlerCriaturas:

    def __init__(self):
        self.azul = 0
        self.rojo = 0
        self.ronda = 0
        self.jugadores = {}
        self.enemigos = {}
        
    def addJugador(self, jugador):
        self.jugadores[jugador.getId()] = jugador
        
    def addEnemigo(self, enemigo):
        self.enemigos[enemigo.getId()] = enemigo
        
    def getJugadores(self):
        return self.jugadores.values()
        
    def getEnemigos(self):
        return self.enemigos.values()
              
    def getCriaturaById(self, id):
        if self.jugadores.has_key(id):
            return self.jugadores[id]
        elif self.enemigos.has_key(id):
            return self.enemigos[id]
        else:
            print("Id invalida:" + str(id))
            return None

    def delCriaturaById(self, id):
        if self.jugadores.has_key(id):
            self.jugadores.pop(id)
        elif self.enemigos.has_key(id):
            self.enemigos.pop(id)
        else:
            print("Id invalida:" + str(id))

    def resetTodos(self):
        [j.reset() for j in self.jugadores.values()]
        
    def setScore(self, azul, rojo, ronda):
        self.azul = azul
        self.rojo = rojo
        self.ronda = ronda


class Criatura(Objeto):

    def __init__(self, id, x, y, vida, vida_max, equipo):
        Objeto.__init__(self, x, y)
        self.id = id
        self.vida = Vida(vida, vida_max)
        self.equipo = equipo
        self.vivo = True
        
    def getId(self):
        return self.id
        
    def esId(self, id):
        return self.id == id
        
    def getEquipo(self):
        return self.equipo
        
    def esEquipo(self, equipo):
        return self.equipo == equipo
        
    def getVida(self):
        return self.vida.get()
        
    def reset(self):
        self.vivo = True
        self.vida.llenar()
        
    def esPrincipal(self):
        return False
        
    def estaVivo(self):
        return self.vivo
        
    def hit(self, danio):   
        self.vida.hit(danio)
        
    def mover(self, x, y):
        self.update(x, y)        
        
    def matar(self):
        self.vivo = False


class Jugador(Criatura):      
    
    def __init__(self, id, x, y, vida, vida_max, equipo):
        Criatura.__init__(self, id, x, y, vida, vida_max, equipo)        
        
        
class Principal(Jugador):
    ''' Esta clase se utiliza para el jugador que esta siendo directamente usado por el cliente. '''
    
    def __init__(self, id, x, y, vida, vida_max, equipo):
        Jugador.__init__(self, id, x, y, vida, vida_max, equipo)
        
    def esPrincipal(self):
        return True


class Vida:
    
    def __init__(self, vida, max):
        self.max = max
        self.actual = vida
        
    def hit(self, cant):
        if self.actual - cant <= 0:
            self.actual = 0
        else:
            self.actual -= cant
        
    def llenar(self):
        self.actual = self.max
        
    def get(self):
        return self.actual