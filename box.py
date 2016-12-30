from coordinate import Coordinate

class Box:

    def __init__(self, coord):
        self.coord = coord

    def __hash__(self):
        return hash(self.coord)
