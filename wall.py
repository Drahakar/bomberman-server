import json

class Wall:
    def __init__(self, coord=None):
        self.coord = coord

    def ascii(self):
        return "|"

    def to_json(self):
        return self.coord.to_json()
