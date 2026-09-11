class PlayerDoesNotExist(Exception):
    pass


class InvalidMovementDirection(Exception):
    pass


class InvalidShootDirection(Exception):
    pass


class InvalidTeam(Exception):
    details = "Team value provided is invalid."


class BlockedPosition(Exception):
    pass


class CantShoot(Exception):
    pass


class CantMove(Exception):
    pass


class RespawnFull(Exception):
    details = "No available space to respawn. Try again later."
