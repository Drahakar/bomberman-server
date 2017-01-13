from bomb import Bomb
from fire_event import FireEvent
from bomb_event import BombEvent
from itertools import groupby
from player import Player
from powerups import Powerup
from random import choice
from time import time
from timer import Periodic
from world_map import WorldMap
import json
import logging
import utils
import powerups

class Game:
    def __init__(self, players, ais, width=11, height=11):
        self.players = players
        self.ais = ais
        self.world_map = WorldMap(width, height, set(players.values()))
        self.acquired_moves = {}
        self.last_tick = None
        self.ticks = 0
        self.ended = False
        self.dead_players = []
        self.ticker = Periodic(self.tick, 3)

    def start(self):
        # self.ticker.start()
        pass

    def tick_handler(self, force=False):
        if not force:
            if len(self.acquired_moves) == len(self.world_map.players) - self.ais: #temporary ai fix
                self.tick()
        else:
            if not time() - self.last_tick > 3:
                return
            self.tick()
        self.last_tick = time()

    def tick(self):
        self.ticks += 1
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
            player.tick()
            if player.coord in all_fire_coords and not player.invincible:
                hp = player.hit()
                logging.info("Player {} is hit. Current HP: {}".format(player.name, player.hp))
                if not hp:
                    self.kill_player(player)

        self.register_player_moves()
        if len(self.world_map.players) <= 1:
            self.ended = True
            self.send_result_to_players()
        else:
            self.send_map_to_players()
            self.acquired_moves = {}

    def register_player_moves(self):
        for client, player in self.players.items():

            try:
                direction, plant_bomb = self.acquired_moves[client]
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

    def create_leaderboard(self):
        result = []

        if self.world_map.players: # Put winner first
            result.append((1, self.world_map.players.pop()))
        else:
            for key, value in groupby(self.dead_players[::-1], lambda x: x[1]):
                place = len(result) + 1
                for _, _, player in value:
                    result.append((place, player))

        return result

    def kill_player(self, player):
        if not self.dead_players:
            self.dead_players.append((self.ticks, 0, player))
        else:
            prev_tick, i, _ = self.dead_players[-1]
            if self.ticks == prev_tick:
                kill_num = i
            else:
                kill_num = i + 1
            self.dead_players.append((self.ticks, kill_num, player))

        self.world_map.remove_player(player)

    def send_map_to_players(self):
        for client, player in self.players.items():
            if player in self.world_map.players:
                client.manual_output("{}".format(self.world_map.to_ascii()))

    def send_result_to_players(self):
        outp = {'event' : 'game_end'}
        self.leaderboard = ["{}: {}".format(place, player) for place, player in self.create_leaderboard()]
        outp['leaderboard'] = self.leaderboard
        for client in self.players:
            client.manual_output(json.dumps(outp, indent=True))

    def get_player_move(self, client, move):
        if self.players[client].hp:
            self.acquired_moves[client] = move
