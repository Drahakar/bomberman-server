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


    def tick(self, game_map, event=None):
        self.life -= 1
        # Check if alive or not
        if not self.life or event == BombEvent.EXPLODE:
            return self.explode(game_map)

        # Movement of bomb
        if event in Bomb.event_to_movement:
            self.move_direction = Bomb.event_to_movement[event]
        self.coord += self.move_direction
        return event

    def explode(self, game_map):
        fire_tiles = {self.coord}
        # Calculate all tiles who will be affected by explosion
        for d in [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]:
            for i in range(1, self.power):
                current_coord = self.coord + (d.x * i, d.y * i)
                tile_type = game_map.get_tile_at(current_coord)
                if tile_type in ["empty", "player"]:
                    fire_tiles.add(current_coord)
                else:
                    break
        fire_id = game_map.get_new_id(Fire)
        game_map.fires[fire_id] = Fire(fire_id, self.owner, fire_tiles)
        del(game_map.bombs[self.bomb_id])
        return game_map.fires[fire_id]
