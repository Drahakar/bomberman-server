import utils
import logging
from directions import Direction
from bomb_event import BombEvent
from fire import Fire

class Bomb:
    event_to_movement = {
        BombEvent.PUSH_LEFT : Direction.LEFT,
        BombEvent.PUSH_RIGHT : Direction.RIGHT,
        BombEvent.PUSH_UP : Direction.UP,
        BombEvent.PUSH_DOWN : Direction.DOWN,
        BombEvent.STOP : Direction.STAY
    }

    def __init__(self, bomb_id, player, life=5):
        self.bomb_id = bomb_id
        self.owner = player
        self.coord = player.coord
        self.life = life
        self.power = player.power
        self.move_direction = (0, 0)


    def tick(self, event=None):
        self.life -= 1
        if not self.life:
            return BombEvent.EXPLODE

        if event in Bomb.event_to_movement:
            self.move_direction = Bomb.event_to_movement[event]
        self.coord += self.move_direction
        return event
    def ascii(self):
        return "b"
