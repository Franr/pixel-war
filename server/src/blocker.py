from twisted.internet import reactor


class Blocker(object):

    def __init__(self, secs):
        self.secs = secs
        self.bloq = True
        self.call_id = reactor.callLater(self.secs, self.unblock)

    def unblock(self):
        self.bloq = False
