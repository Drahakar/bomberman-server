from player import Player
from bomb import Bomb
from world_map import WorldMap
from time import time
from timer import Periodic
import logging
import utils

class Game:
    def __init__(self, players, ais, width=11, height=11):
        self.players = players
        for i in range(ais):
            self.players.append(Player("Bot"))
        self.ais = ais
        self.world_map = WorldMap(width, height, players)
        self.players = self.world_map.players
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
            bomb.tick(self.world_map)

        for fire in list(self.world_map.fires.values()):
            fire.tick(self.world_map)

        self.register_player_moves()

    def register_player_moves(self):
        for player in self.players:
            direction, plant_bomb = self.acquired_moves[player]

            # Movement
            coord_offset = utils.direction_as_movement_delta(direction)
            dest_coord = player.coord + coord_offset
            if self.world_map.can_move_to(dest_coord, coord_offset):
                player.coord = dest_coord

            # Bomb
            if plant_bomb and player.num_bombs >= 0:
                bomb_id = self.world_map.get_new_id(Bomb)
                self.world_map.bombs[bomb_id] = Bomb(bomb_id, player.coord, player.power)

    def get_player_move(self, player, move):
        self.acquired_moves[player] = move
