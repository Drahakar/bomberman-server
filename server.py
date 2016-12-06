import logging
from player import Player
from game import Game
import asyncio
import websockets
import json
import uuid
from time import time
from websockets.exceptions import ConnectionClosed

class Server:
    def __init__(self, loglevel, listen_host, listen_port):
        self.host = listen_host
        self.port = listen_port
        self.clients = set()
        self.registered_players = {}
        self.player_game = {}
        self.games = set()
        logging.basicConfig(format="%(asctime)s %(levelname)s  %(message)s", level=loglevel)
        self.types = {
            "register" : self.register_player,
            "start_game" : self.start_game,
            "move" : self.register_move,
        }


    def start(self):
        start_server = websockets.serve(self.request_handler, self.host, self.port)

        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    @asyncio.coroutine
    def request_handler(self, websocket, path):
        self.clients.add(websocket)

        while True:
            try:
                start = time()
                msg = yield from websocket.recv()
                response_time = time() - start
                logging.info("Client took {} to respond".format(time() - start))
                logging.info("Message recieved: {}".format(msg))
                logging.info("Connected clients: {}".format(len(self.clients)))
                logging.info("Registered players: {}".format(self.registered_players))
                # if self.time_handler(response_time, websocket):
                    # yield from websocket.send("WARNING: you're too slow")
                # else:
                    # yield from self.message_handler(msg, websocket)
                yield from self.message_handler(msg, websocket)
            except ConnectionClosed as e:
                self.clients.remove(websocket)
                if websocket in self.registered_players:
                    del(self.registered_players[websocket])
                logging.info("Removed connection. Current connections: {}".format(len(self.clients)))
                break

    def time_handler(self, response_time, websocket):
        return response_time > 3 and websocket in self.player_game

    def message_handler(self, message, websocket):
        try: 
            message = json.loads(message)
            return self.types[message["type"]](message, websocket)
        except (ValueError, KeyError) as e:
            return websocket.send("Invalid request: {}".format(e))

    def register_player(self, message, websocket):
        if websocket in self.registered_players:
            return websocket.send("Player already registered")
        else:
            self.registered_players[websocket] = Player(message["name"])
            return websocket.send("Player registered")

    def start_game(self, message, websocket):
        if websocket in self.player_game:
            return websocket.send("Can't play two games at once")
        game = Game([self.registered_players[websocket]], 0)
        self.player_game[websocket] = game
        self.games.add(game)
        game.start()
        return websocket.send("{}\n{}".format(game.world_map.to_json(), game.world_map.to_ascii()))

    def register_move(self, message, websocket):
        if websocket not in self.player_game:
            return websocket.send("You are not in a game")
        current_player = self.registered_players[websocket]
        current_game = self.player_game[websocket]
        current_game.get_player_move(current_player, message["direction"])
        current_game.tick()
        return websocket.send("{}\n{}".format(current_game.world_map.to_json(), current_game.world_map.to_ascii()))
