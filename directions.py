from coordinate import Coordinate
class Direction:
    LEFT = Coordinate(-1, 0)
    RIGHT = Coordinate(1, 0)
    DOWN = Coordinate(0, -1)
    UP = Coordinate(0, 1)
    STAY = Coordinate(0, 0)

    @staticmethod
    def all():
        return {Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN, Direction.STAY}
