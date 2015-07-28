import time

from twisted.internet import reactor


class Bloqueo(object):

    def __init__(self, tiempo):
        self.tiempo = tiempo
        self.bloq = False

    def block_me(self):
        self.bloq = True
        time.sleep(self.tiempo)
        self.bloq = False


class BloqueoMov(Bloqueo):

    def __init__(self):
        Bloqueo.__init__(self, 0.15)
        reactor.callInThread(self.block_me)


class BloqueoDisp(Bloqueo):

    def __init__(self):
        Bloqueo.__init__(self, 0.10)
        reactor.callInThread(self.block_me)
