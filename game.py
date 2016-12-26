from bomb import Bomb
from fire_event import FireEvent
from player import Player
from time import time
from timer import Periodic
from world_map import WorldMap
import logging
import utils

class Game:
    def __init__(self, players, ais, width=11, height=11):
        self.players = players
        self.ais = ais
        self.world_map = WorldMap(width, height, players.values())
        self.acquired_moves = {}
        self.last_tick = None
        self.ticker = Periodic(self.tick, 3)

    def start(self):
        # self.ticker.start()
        pass

    def tick_handler(self, force=False):
        if not force:
            if len(self.acquired_moves) == len(self.players) - self.ais: #temporary ai fix
                self.tick()

        else:
            if not time() - self.last_tick > 3:
                return
            self.tick()
        self.last_tick = time()

    def tick(self):
        logging.info("TICKING")
        for bomb in list(self.world_map.bombs.values()):
            bomb.tick(self.world_map)

        # Union all fire coordinates into a set
        all_fire_coords = set()
        for fire in list(self.world_map.fires.values()):
            if fire.tick(self.world_map) != FireEvent.BURN_OUT:
                all_fire_coords = all_fire_coords.union(fire.coords)
            else:
                fire.owner.num_bombs += 1

        # Try to blow up all bombs, including spawning new fire for the blown up
        # bombs. Keep looping until no bomb has exploded within the loop.
        bombs_exploded = True
        while bombs_exploded:
            bombs_exploded = False
            for bomb in list(self.world_map.bombs.values()):
                if bomb.coord in all_fire_coords:
                    new_fire = bomb.explode(self.world_map)
                    new_fire.tick(self.world_map) # Tick new fire to match the triggering fire.
                    all_fire_coords = all_fire_coords.union(new_fire.coords)
                    bombs_exploded = True

        for player in self.players.values():
            if player.coord in all_fire_coords:
                logging.info("Player {} is in fire {}".format(player.name, fire.fire_id))

        self.register_player_moves()
        self.send_map_to_players()
        self.acquired_moves = {}

    def register_player_moves(self):
        for player_client, player in self.players.items():
            direction, plant_bomb = self.acquired_moves[player_client]

            # Movement
            try:
                coord_offset = utils.direction_as_movement_delta(direction)
                dest_coord = player.coord + coord_offset
                if self.world_map.can_move_to(dest_coord, coord_offset):
                    player.coord = dest_coord

                # Bomb
                if plant_bomb and player.num_bombs > 0:
                    bomb_id = self.world_map.get_new_id(Bomb)
                    self.world_map.bombs[bomb_id] = Bomb(bomb_id, player)
                    player.num_bombs -= 1
            except KeyError:
                pass

    def send_map_to_players(self):
        for client in self.players:
            client.manual_output("{}\n{}".format(self.world_map.to_json(), self.world_map.to_ascii()))

    def get_player_move(self, player, move):
        self.acquired_moves[player] = move
