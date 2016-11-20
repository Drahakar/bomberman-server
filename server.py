import logging
from player import Player
from game import Game
import asyncio
import websockets
import json
import uuid
from websockets.exceptions import ConnectionClosed

class Server:
    def __init__(self, loglevel, listen_host, listen_port):
        self.host = listen_host
        self.port = listen_port
        self.clients = set()
        self.registered_players = {}
        self.games = set()
        logging.basicConfig(format="%(asctime)s %(levelname)s  %(message)s", level=loglevel)
        self.types = {
            "register" : self.register_player,
            "start_game" : self.start_game
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
                msg = yield from websocket.recv()
                logging.info("Message recieved: {}".format(msg))
                logging.info("Connected clients: {}".format(len(self.clients)))
                logging.info("Registered players: {}".format(self.registered_players))
                status, retmsg = self.message_handler(msg, websocket)
                yield from websocket.send(retmsg)
            except ConnectionClosed as e:
                self.clients.remove(websocket)
                if websocket in self.registered_players:
                    del(self.registered_players[websocket])
                logging.info("Removed connection. Current connections: {}".format(len(self.clients)))
                break

    def message_handler(self, message, websocket):
        try: 
            message = json.loads(message)
            return self.types[message["type"]](message, websocket)
        except ValueError as e:
            return "error", "Invalid request: {}".format(e)

    def register_player(self, message, websocket):
        self.registered_players[websocket] = Player(message["name"])
        return "success", "Player registered"


    def start_game(self, message, websocket):
        game = Game([self.registered_players[websocket]], 3)
        self.games.add(game)
        return "success", "{}\n{}".format(game.to_json(), game.to_ascii())
