from coordinate import Coordinate
import config
import json

class Box:

    def __init__(self, coord):
        self.coord = coord
        self.time_until_removal = config.FIRE_DURATION + 1

    def tick(self):
        self.time_until_removal -= 1
        return self.time_until_removal

    def to_json(self):
        return self.coord.to_json()

    def ascii(self):
        return "X"

    def __hash__(self):
        return hash(self.coord)
