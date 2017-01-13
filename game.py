from bomb import Bomb
from fire_event import FireEvent
from bomb_event import BombEvent
from player import Player
from powerups import Powerup
from random import choice
from time import time
from timer import Periodic
from world_map import WorldMap
import logging
import utils
import powerups

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
        for bomb in list(self.world_map.bombs.values()):
            if bomb.tick() == BombEvent.EXPLODE:
                self.world_map.explode_bomb(bomb)
            else:
                if bomb.is_moving() and self.world_map.can_move_to(bomb.coord, bomb.move_direction):
                    self.world_map.move_bomb(bomb)

        # Union all fire coordinates into a set
        all_fire_coords = set()
        for fire in list(self.world_map.fires):
            if fire.tick() != FireEvent.BURN_OUT:
                all_fire_coords = all_fire_coords.union(fire.coords)
            else:
                self.world_map.remove_fire(fire)

        # Try to blow up all bombs, including spawning new fire for the blown up
        # bombs. Keep looping until no bomb has exploded within the loop.
        bombs_exploded = True
        while bombs_exploded:
            bombs_exploded = False
            for bomb in list(self.world_map.bombs.values()):
                if bomb.coord in all_fire_coords:
                    new_fire = self.world_map.explode_bomb(bomb)
                    new_fire.tick() # Tick new fire to match the triggering fire.
                    all_fire_coords = all_fire_coords.union(new_fire.coords)
                    bombs_exploded = True

        for player in self.players.values():
            if player.coord in all_fire_coords:
                logging.info("Player {} is in fire".format(player.name, fire))
            player.tick()
            if player.coord in all_fire_coords and not player.invincible:

        self.register_player_moves()
        self.send_map_to_players()
        self.acquired_moves = {}

    def register_player_moves(self):
        for player_client, player in self.players.items():
            direction, plant_bomb = self.acquired_moves[player_client]

            try:
                # Movement
                direction = utils.direction_as_movement_delta(direction)
                dest_coord = player.coord + direction
                target_tile = self.world_map.get_classes_at(dest_coord)

                if Bomb in target_tile and player.can_push_bombs:
                    self.world_map.bombs[dest_coord].set_movement(direction)
                elif self.world_map.can_move_to(player.coord, direction):
                    if Powerup in target_tile:
                        self.world_map.use_powerup(dest_coord, player)
                    self.world_map.move_object(player, player.coord, dest_coord)

                # Bomb
                target_tile = self.world_map.get_classes_at(player.coord)
                if plant_bomb and player.num_bombs > 0 and not Bomb in target_tile:
                    self.world_map.add_new_bomb(player)
            except KeyError:
                pass

    def send_map_to_players(self):
        for client in self.players:
            client.manual_output("{}".format(self.world_map.to_ascii()))

    def get_player_move(self, player, move):
        self.acquired_moves[player] = move
