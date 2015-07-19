import threading
import time


class Bloqueo(threading.Thread):

    def __init__(self, tiempo):
        threading.Thread.__init__(self)
        self.tiempo = tiempo
        self.bloq = True

    def run(self):
        time.sleep(self.tiempo)
        self.bloq = False


class BloqueoMov(Bloqueo):

    def __init__(self):
        Bloqueo.__init__(self, 0.15)
        self.start()


class BloqueoDisp(Bloqueo):

    def __init__(self):
        Bloqueo.__init__(self, 0.10)
        self.start()
