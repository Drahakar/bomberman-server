from game import config
from game.assets import *
from game.assets.powerups import Powerup
from utils import Coordinate, Direction

from random import sample, shuffle, choice
import json
import logging


class WorldMap:
    def __init__(self, width, height, players):
        self.width = width
        self.height = height
        self.players = players
        self.tiles = self.make_tiles()

        self.spawn_players()
        self.gen_initial_entities()

        self.bombs = {}
        self.fires = set()
        self.powerups = {}

    def make_tiles(self):
        tiles = {}
        for x in range(self.width):
            for y in range(self.height):
                tiles[Coordinate(x,y)] = Tile()
        return tiles

    def spawn_players(self):
        for player, spawn_point in zip(self.players, self.gen_spawn_points()):
            self.tiles[spawn_point].add(player)
            player.coord = spawn_point

    def gen_spawn_points(self):
        possible_spawns = [
            Coordinate(0,0),
            Coordinate(self.width - 1, 0),
            Coordinate(0, self.height - 1),
            Coordinate(self.width - 1, self.height - 1)
        ]
        # Comment out shuffle while developing
        # shuffle(possible_spawns)
        return possible_spawns

    def gen_initial_entities(self):
        self.walls = set()
        wall_coords = set()
        for x in range(1, self.width, 2):
            for y in range(1, self.height, 2):
                new_coord = Coordinate(x,y)
                new_wall = Wall(new_coord)

                wall_coords.add(new_coord)
                self.tiles[new_coord].content.add(new_wall)
                self.walls.add(new_wall)
        self.gen_boxes(wall_coords)

    def gen_boxes(self, skip):
        self.boxes = {}
        possible_box_coords = set()
        for x in range(self.width):
            for y in range(self.height):
                possible_box_coords.add(Coordinate(x,y))
        possible_box_coords -= skip

        for player in self.players:
            for d in Direction.all():
                try:
                    possible_box_coords.remove(player.coord - (d.x, d.y))
                    possible_box_coords.remove(player.coord - (2 * d.x, 2 * d.y))
                except KeyError:
                    pass
        box_coords = sample(
            possible_box_coords,
            round(len(possible_box_coords) * config.BOX_DENSITY))
        for coord in box_coords:
            new_box = Box(coord)
            self.boxes[coord] = new_box
            self.tiles[coord].add(new_box)

    def move_object(self, obj, src_coord, dest_coord):
        self.tiles[src_coord].remove(obj)
        self.tiles[dest_coord].add(obj)
        obj.coord = dest_coord

    def move_bomb(self, bomb):
        del(self.bombs[bomb.coord])
        self.bombs[bomb.next_coord()] = bomb
        self.move_object(bomb, bomb.coord, bomb.next_coord())

    def add_new_fire(self, player, coord):
        fire_coords = self.get_fire_coords(coord, player.power)
        new_fire = Fire(player, fire_coords)
        for coord in fire_coords:
            self.tiles[coord].add(new_fire)
        self.fires.add(new_fire)
        return new_fire

    def add_new_bomb(self, player):
        player.num_bombs -= 1
        bomb_id = 0 if not self.bombs else max(bomb.id for bomb in self.bombs.values()) + 1
        bomb = Bomb(bomb_id, player)
        self.tiles[player.coord].add(bomb)
        self.bombs[player.coord] = bomb

    def remove_fire(self, fire):
        fire.owner.num_bombs += 1
        for coord in fire.coords:
            self.tiles[coord].remove(fire)
            if Box in self.get_classes_at(coord):
                self.open_box(coord)
        self.fires.remove(fire)

    def remove_player(self, player):
        self.players.remove(player)
        self.tiles[player.coord].remove(player)

    def open_box(self, coord):
        box = self.boxes[coord]
        del(self.boxes[coord])
        self.tiles[coord].remove(box)

        self.add_powerup(coord)

    def add_powerup(self, coord):
        powerup = choice(powerups.all())(coord)
        self.powerups[coord] = powerup
        self.tiles[coord].add(powerup)

    def use_powerup(self, coord, player=None):
        powerup = self.powerups[coord]
        if player:
            logging.info("Player {} picked up {}".format(
                player.name,
                powerup.__class__.__name__)
            )
            powerup.use(player)
        self.tiles[coord].remove(powerup)
        del(self.powerups[coord])

    def explode_bomb(self, bomb):
        fire = self.add_new_fire(bomb.owner, bomb.coord)
        self.tiles[bomb.coord].remove(bomb)
        del(self.bombs[bomb.coord])
        return fire

    def get_fire_coords(self, coord, power):
        fire_coords = {coord}
        for d in [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]:
            for i in range(1, power):
                current_coord = coord + (d.x * i, d.y * i)
                tile_classes = self.get_classes_at(current_coord)
                if not Wall in tile_classes:
                    fire_coords.add(current_coord)
                    if Box in tile_classes:
                        break
                    if Powerup in tile_classes:
                        self.use_powerup(current_coord)
                else:
                    break
        return fire_coords

    def all_fire_coords(self):
        """Union all fire coordinates together and return a new set with all those"""
        if self.fires:
            return set.union(*[fire.coords for fire in self.fires])
        else:
            return set()

    def json_compatible(self):
        ret = {}
        jsonfunc = lambda x: x.json_compatible()
        ret["width"]    = self.width
        ret["height"]   = self.height
        ret["walls"]    = list(map(jsonfunc, self.walls))
        ret["players"]  = list(map(jsonfunc, self.players))
        ret["bombs"]    = list(map(jsonfunc, self.bombs))
        ret["boxes"]    = list(map(jsonfunc, self.boxes))
        ret["powerups"] = list(map(jsonfunc, self.powerups))
        ret["fires"]    = list(map(jsonfunc, self.all_fire_coords()))
        return ret

    def to_json(self):
        return json.dumps(self.json_compatible())

    def to_ascii(self):
        asc_map = [[" " for x in range(self.width)] for y in range(self.height)]
        for x in range(self.width):
            for y in range(self.height):
                for c in self.tiles[Coordinate(x,y)].content:
                    asc_map[y][x] = c.ascii()
        # Frame
        for row in asc_map:
            row.insert(0, "|")
            row.append("|")
        asc_map.insert(0, ["-"] * (self.width + 2))
        asc_map.append(["-"] * (self.width + 2))
        return '\n'.join([''.join(row) for row in asc_map])

    def pos_to_coord(self, pos):
        y = pos // self.width
        x = pos % self.width
        return Coordinate(x, y)

    def coord_to_pos(self, coord):
        return coord.y * self.width + coord.x

    def inside_map(self, coord):
        return 0 <= coord.x <= self.width - 1 and 0 <= coord.y <= self.height - 1

    def get_tile_at(self, coord):
        if self.inside_map(coord):
            return tuple(self.tiles[coord].content)
        else:
            return (Wall(),)

    def get_classes_at(self, coord):
        if self.inside_map(coord):
            return tuple(self.tiles[coord].content_classes())
        else:
            return (Wall,)

    def can_move_to(self, coord, direction=Direction.STAY):
        valid_tiles = (Player, Powerup, Fire)
        target_tile = self.get_tile_at(coord + direction)
        return not target_tile or any(isinstance(c, valid_tiles) for c in target_tile)
