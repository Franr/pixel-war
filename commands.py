from twisted.protocols.amp import Command, String, Integer, ListOf


class Move(Command):
    arguments = [('id', Integer()),
                 ('dir', String())]
    response = [('ok', Integer())]


class MoveObject(Command):
    arguments = [('id', Integer()),
                 ('x', Integer()),
                 ('y', Integer())]
    response = [('ok', Integer())]


class ID(Command):
    arguments = [('id', Integer())]
    response = [('ok', Integer())]


class SendMap(Command):
    arguments = [('sec_map', String())]  # use dict maybe?
    response = [('ok', Integer())]


class CreateObject(Command):
    arguments = [('obj_data', ListOf(Integer()))]
    response = [('ok', Integer())]


class Login(Command):
    arguments = [('team', Integer())]
    response = [('ok', Integer())]


class PlayerReady(Command):
    arguments = [('id', Integer())]
    response = [('ok', Integer())]


class PlayerShoot(Command):
    # create a shot on the clients
    arguments = [('id', Integer()),
                 ('dir', String()),
                 ('x', Integer()),
                 ('y', Integer())]
    response = [('ok', Integer())]


class Shoot(Command):
    # send shoot action to the server
    arguments = [('id', Integer()),
                 ('dir', String())]
    response = [('ok', Integer())]
