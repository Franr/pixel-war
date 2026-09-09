class Team:
    BLUE = 1
    RED = 2
    LIST = (BLUE, RED)


class Direction:
    # TODO: replace "o" with "w"
    # 2 axis
    NORTH = "n"
    SOUTH = "s"
    WEST = "o"
    EAST = "e"

    # 4 axis
    NORTH_WEST = "no"
    NORTH_EAST = "ne"
    SOUTH_WEST = "so"
    SOUTH_EAST = "se"

    @classmethod
    def validate_2(cls, dir: str) -> bool:
        return dir in (cls.NORTH, cls.SOUTH, cls.WEST, cls.EAST)

    @classmethod
    def validate_4(cls, dir: str) -> bool:
        return cls.validate_2(dir) or \
            dir in (cls.NORTH_WEST, cls.NORTH_EAST, cls.SOUTH_WEST, cls.SOUTH_EAST)
