from bomb import Bomb
from box import Box
from coordinate import Coordinate
from directions import Direction
from fire import Fire
from player import Player
from powerups import Powerup
from random import sample, shuffle, choice
from tile import Tile
from wall import Wall
import config
import json
import logging
import powerups

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
            player.alive = True

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
        wall_coords = set()
        for x in range(1, self.width, 2):
            for y in range(1, self.height, 2):
                wall_coords.add(Coordinate(x,y))
                self.tiles[Coordinate(x,y)].content.add(Wall())
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
        bomb = Bomb(player)
        self.tiles[player.coord].add(bomb)
        self.bombs[player.coord] = bomb

    def remove_fire(self, fire):
        fire.owner.num_bombs += 1
        for coord in fire.coords:
            self.tiles[coord].remove(fire)
            if Box in self.get_classes_at(coord):
                self.open_box(coord)
        self.fires.remove(fire)


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
        valid_tiles = (Player, Powerup)
        target_tile = self.get_tile_at(coord + direction)
        return not target_tile or any(isinstance(c, valid_tiles) for c in target_tile)
