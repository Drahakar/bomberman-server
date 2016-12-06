from uuid import uuid4
from bomb import Bomb

class Player:
    def __init__(self, name):
        self.name = name
        self.p_id = str(uuid4())
        self.setup()

    def setup(self):
        self.coord = None
        self.alive = True
        self.num_bombs = 1
        self.power = 3

    def __str__(self):
        return "Name: {}, id: {}".format(self.name, self.p_id)

    def __repr__(self):
        return "Name: {}, id: {}".format(self.name, self.p_id)
