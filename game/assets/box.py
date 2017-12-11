from game import config
from utils import Coordinate

import json


class Box:

    def __init__(self, coord):
        self.coord = coord
        self.time_until_removal = config.FIRE_DURATION + 1

    def tick(self):
        self.time_until_removal -= 1
        return self.time_until_removal

    def json_compatible(self):
        return self.coord.json_compatible()

    def ascii(self):
        return "X"

    def __hash__(self):
        return hash(self.coord)
