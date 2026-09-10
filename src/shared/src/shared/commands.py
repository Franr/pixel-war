from dataclasses import dataclass


@dataclass
class Command:
    pass

####################
# Server to client #
####################

@dataclass
class SendMap(Command):
    sec_map: list[list[int]]
    action: str = "send_map"

@dataclass
class CreateObject(Command):
    obj_data: list[int]
    correlation_id: str
    action: str = "create_object"

@dataclass
class CreateObjects(Command):
    objs_data: list[list[int]]
    action: str = "create_objects"

@dataclass
class UpdateScore(Command):
    blue: int
    red: int
    action: str = "update_score"

@dataclass
class MoveObject(Command):
    uid: int
    x: int
    y: int
    action: str = "move_object"

@dataclass
class PlayerShoot(Command):
    uid: int
    direction: str
    x: int
    y: int
    action: str = "player_shoot"

@dataclass
class PlayerHit(Command):
    uid: int
    dmg: int
    action: str = "player_hit"

@dataclass
class PlayerRevive(Command):
    uid: int
    action: str = "player_revive"

@dataclass
class PlayerLogout(Command):
    uid: int
    action: str = "player_logout"

@dataclass
class ServerError(Command):
    description: str
    action: str = "server_error"

####################
# Client to server # 
####################

@dataclass
class Login(Command):
    team: int
    correlation_id: str
    action: str = "login"

@dataclass
class Move(Command):
    uid: int
    direction: str
    action: str = "move"

@dataclass
class Shoot(Command):
    uid: int
    direction: str
    action: str = "shoot"

# class RestartRound(Command):
#     arguments = [('uid', Integer())]
#     response = [('ok', Integer())]
