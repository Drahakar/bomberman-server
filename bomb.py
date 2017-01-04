import config
import utils
import logging
from directions import Direction
from bomb_event import BombEvent
from fire import Fire

class Bomb:
    def __init__(self, player, life=config.BOMB_TIMER):
        self.owner = player
        self.coord = player.coord
        self.life = life
        self.power = player.power
        self.move_direction = Direction.STAY

    def set_movement(self, direction):
        self.move_direction = direction

    def is_moving(self):
        return self.move_direction != Direction.STAY

    def next_coord(self):
        return self.coord + self.move_direction

    def tick(self):
        self.life -= 1
        if not self.life:
            return BombEvent.EXPLODE

    def ascii(self):
        return "b"
