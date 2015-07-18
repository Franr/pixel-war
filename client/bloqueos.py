import threading
import time


class Bloqueo(threading.Thread):

    def __init__(self, delay):
        threading.Thread.__init__(self)
        self.delay = delay
        self.bloquear()
        self.start()
        
    def bloquear(self):
        self.__class__.block = True
        
    def desbloquear(self):
        self.__class__.block = False
    
    def run(self):
        time.sleep(self.delay)
        self.desbloquear()


class BloqueoMov(Bloqueo):

    block = False
    
    def __init__(self):
        Bloqueo.__init__(self, 0.15)


class BloqueoDisp(Bloqueo):
    
    block = False
    
    def __init__(self):
        Bloqueo.__init__(self, 0.10)
