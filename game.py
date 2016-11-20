import json
from random import shuffle
from player import Player

class Game:
    def __init__(self, players, ais, width=11, height=11):
        self.players = players
        for i in range(ais):
            self.players.append(Player("Bot"))
        self.width = width
        self.height = height
        for player, spawn_point in zip(self.players, self.gen_spawn_points()):
            player.coordinate = spawn_point
        self.walls = self.gen_walls()

    def gen_spawn_points(self):
        possible_spawns = [
            (0,0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1)
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
                "position" : player.coordinate,
                "alive" : player.alive
                }
            )
        return json.dumps(ret)
            
    def pos_to_coord(self, pos):
        y = pos // self.width
        x = pos % self.width
        return x, y

    def to_ascii(self):
        asc_map = [[" " for x in range(self.width)] for y in range(self.height)] 
        # Walls
        for w in self.walls:
            w_x, w_y = self.pos_to_coord(w)
            asc_map[w_y][w_x] = "w"
        # Players
        for i, p in enumerate(self.players):
            p_x, p_y = p.coordinate
            asc_map[p_y][p_x] = str(i)
        # Frame
        for row in asc_map:
            row.insert(0, "|")
            row.append("|")
        asc_map.insert(0, ["-"] * (self.width + 2))
        asc_map.append(["-"] * (self.width + 2))
        return '\n'.join([''.join(row) for row in asc_map])

