import json

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
            
    def to_json(self):
        return json.dumps({'x' : self.x, 'y' : self.y})

    def __add__(self, tup):
        x, y = tup
        return Coordinate(self.x + x, self.y + y)

    def __sub__(self, tup):
        x, y = tup
        return Coordinate(self.x - x, self.y - y)

    def __mul__(self, tup):
        x, y = tup
        return Coordinate(self.x * x, self.y * y)

    def __repr__(self):
        return str((self.x, self.y))

    def __eq__(self, other):
        return isinstance(other, Coordinate) and other.x == self.x and other.y == self.y

    def __hash__(self):
        return hash((self.x, self.y))
