from twisted.internet import reactor


class Bloqueo(object):

    def __init__(self):
        self._block()
        reactor.callLater(self.delay, self._unblock)

    def _block(self):
        self.__class__.block = True

    def _unblock(self):
        self.__class__.block = False


class BloqueoMov(Bloqueo):

    block = False
    delay = 0.15


class BloqueoDisp(Bloqueo):

    block = False
    delay = 0.10
