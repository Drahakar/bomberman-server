from coordinate import Coordinate
from random import shuffle
import json
import logging

class WorldMap:
    def __init__(self, width, height, players):
        self.width = width
        self.height = height
        self.players = players
        self.walls = self.gen_walls()
        for player, spawn_point in zip(self.players, self.gen_spawn_points()):
            player.coord = spawn_point
            player.alive = True

    def gen_spawn_points(self):
        possible_spawns = [
            Coordinate(0,0),
            Coordinate(self.width - 1, 0),
            Coordinate(0, self.height - 1),
            Coordinate(self.width - 1, self.height - 1)
        ]
        shuffle(possible_spawns)
        return possible_spawns

    def gen_walls(self):
        ret = []
        for x in range(1, self.width, 2):
            for y in range(1, self.height, 2):
                ret.append(y * self.width + x)
        return ret

    def to_json(self):
        ret = {}
        ret["map"] = {}
        ret["map"]["width"] = self.width
        ret["map"]["height"] = self.height
        ret["map"]["walls"] = self.walls
        ret["players"] = []
        for player in self.players:
            ret["players"].append({
                "id" : player.p_id,
                "coord" : (player.coord.x, player.coord.y),
                "alive" : player.alive
                }
            )
        return json.dumps(ret)

    def to_ascii(self):
        asc_map = [[" " for x in range(self.width)] for y in range(self.height)] 
        # Walls
        for w in self.walls:
            w_coord = self.pos_to_coord(w)
            asc_map[w_coord.y][w_coord.x] = "w"
        # Players
        for i, p in enumerate(self.players):
            asc_map[p.coord.y][p.coord.x] = str(i)
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
        pos = self.coord_to_pos(coord)
        for p in self.players:
            if coord == p.coord:
                return "player"
        if pos in self.walls:
            return "wall"
        if self.inside_map(coord):
            return "empty"    
        else:
            return "wall"

    def can_move_to(self, coord, direction):
        logging.info("{}".format(self.get_tile_at(coord)))
        # TODO:
        # if tile_type == "bomb": 
        return self.get_tile_at(coord) == "empty"
