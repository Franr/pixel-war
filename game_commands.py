from twisted.protocols.amp import Command, String, Integer, ListOf


class Move(Command):
    arguments = [('uid', Integer()),
                 ('direction', String())]
    response = [('ok', Integer())]


class MoveObject(Command):
    arguments = [('uid', Integer()),
                 ('x', Integer()),
                 ('y', Integer())]
    response = [('ok', Integer())]


class UID(Command):
    arguments = [('uid', Integer())]
    response = [('ok', Integer())]


class SendMap(Command):
    arguments = [('sec_map', ListOf(ListOf(Integer())))]
    response = [('ok', Integer())]


class CreateObject(Command):
    arguments = [('obj_data', ListOf(Integer()))]
    response = [('ok', Integer())]


class CreateObjects(Command):
    arguments = [('obj_data', ListOf(ListOf(Integer())))]
    response = [('ok', Integer())]


class Login(Command):
    arguments = [('team', Integer())]
    response = [('uid', Integer())]


class PlayerShoot(Command):
    # create a shot on the clients
    arguments = [('uid', Integer()),
                 ('direction', String()),
                 ('x', Integer()),
                 ('y', Integer())]
    response = [('ok', Integer())]


class PlayerHit(Command):
    arguments = [('uid', Integer()),
                 ('dmg', Integer())]
    response = [('ok', Integer())]


class PlayerRevive(Command):
    arguments = [('uid', Integer())]
    response = [('ok', Integer())]


class Shoot(Command):
    # send shoot action to the server
    arguments = [('uid', Integer()),
                 ('direction', String())]
    response = [('ok', Integer())]


class LogoutPlayer(Command):
    arguments = [('uid', Integer())]
    response = [('ok', Integer())]


class UpdateScore(Command):
    arguments = [('blue', Integer()),
                 ('red', Integer())]
    response = [('ok', Integer())]


class RestartRound(Command):
    arguments = [('uid', Integer())]
    response = [('ok', Integer())]


class AddBot(Command):
    arguments = [('team', Integer())]
    response = [('ok', Integer())]


class DeleteBot(Command):
    arguments = [('team', Integer())]
    response = [('ok', Integer())]
