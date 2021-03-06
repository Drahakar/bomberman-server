from game import config

from uuid import uuid4
import json


class Player:
    def __init__(self, name):
        self.name = name
        self.p_id = str(uuid4())
        self.setup()

    def setup(self):
        self.coord = None
        self.hp = config.PLAYER_LIVES
        self.invincible = 0
        self.can_push_bombs = False
        self.num_bombs = config.INITIAL_BOMB_AMOUNT
        self.power = config.INITIAL_POWER

    def hit(self):
        self.hp = max(0, self.hp - 1)
        self.invincible = config.INVINCIBLE_FRAMES
        return self.hp

    def tick(self):
        self.invincible = max(0, self.invincible - 1)

    def ascii(self):
        return "p"

    def json_compatible(self):
        ret = {}
        ret['name'] = self.name
        ret['id'] = self.p_id
        ret['invincible'] = self.invincible
        ret['coord'] = self.coord.json_compatible()
        return ret

    def __str__(self):
        return "Name: {}, id: {}".format(self.name, self.p_id)

    def __repr__(self):
        return "Name: {}, id: {}".format(self.name, self.p_id)
