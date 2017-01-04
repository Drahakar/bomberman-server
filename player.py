from uuid import uuid4
from bomb import Bomb
import config

class Player:
    def __init__(self, name):
        self.name = name
        self.p_id = str(uuid4())
        self.setup()

    def setup(self):
        self.coord = None
        self.alive = True
        self.can_push_bombs = False
        self.num_bombs = config.INITIAL_BOMB_AMOUNT
        self.power = config.INITIAL_POWER

    def ascii(self):
        return "p"

    def __str__(self):
        return "Name: {}, id: {}".format(self.name, self.p_id)

    def __repr__(self):
        return "Name: {}, id: {}".format(self.name, self.p_id)
