from twisted.internet import reactor


class Blocker(object):

    def __init__(self):
        self._block = False

    def block(self):
        self._block = True
        reactor.callLater(self.delay, self.unblock)

    def unblock(self):
        self._block = False

    def is_blocked(self):
        return self._block


class MoveBlock(Blocker):
    delay = 0.15


class FireBlock(Blocker):
    delay = 0.10
