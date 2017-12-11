import json


class Wall:
    def __init__(self, coord=None):
        self.coord = coord

    def ascii(self):
        return "|"

    def json_compatible(self):
        return self.coord.json_compatible()
