import logging
import traceback
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
        client = ClientConnect(websocket)
        self.clients.add(client)
        logging.info("Connected clients: {}".format(len(self.clients)))
        while True:
            try:
                # if self.time_handler(response_time, websocket):
                    # yield from websocket.send("WARNING: you're too slow")
                # else:
                    # yield from self.message_handler(msg, websocket)

                listener_task = asyncio.ensure_future(client.get_message())
                sender_task = asyncio.ensure_future(client.prepare_send())
                done, pending = yield from asyncio.wait(
                    [listener_task, sender_task],
                    return_when=asyncio.FIRST_COMPLETED)

                if listener_task in done:
                    yield from client.parse_incoming(self)
                else:
                    listener_task.cancel()

                if sender_task in done:
                    msg_to_send = sender_task.result()
                    if msg_to_send:
                        yield from client.send_message(msg_to_send)
                else:
                    sender_task.cancel()

            except ConnectionClosed as e:
                self.clients.remove(client)
                if websocket in self.registered_players:
                    del(self.registered_players[client])
                logging.info("Removed connection. Current connections: {}".format(len(self.clients)))
                break

    def time_handler(self, response_time, websocket):
        return response_time > 3 and websocket in self.player_game

    def message_handler(self, message, client):
        try: 
            message = json.loads(message)
            return self.types[message["type"]](message, client)
        except (ValueError, KeyError) as e:
            logging.debug(traceback.print_exc())
            return "Invalid request: {}".format(e)

    def register_player(self, message, client):
        if client in self.registered_players:
            return "Player already registered"
        else:
            self.registered_players[client] = Player(message["name"])
            # if len(self.registered_players) == 1:
                # self.start_game()
            logging.info("Registered players: {}".format(self.registered_players))
            return "Player registered"

    def register_move(self, message, client):
        if client not in self.player_game:
            return "You are not in a game"
        current_player = self.registered_players[client]
        current_game = self.player_game[client]
        current_game.get_player_move(client, (message["direction"], message["plant_bomb"]))
        current_game.tick_handler()

    def start_game(self, a=1, b=1):
        game = Game(self.registered_players, 0)
        logging.info("Starting game")
        for player in self.registered_players:
            self.player_game[player] = game
        for client in self.registered_players:
            client.manual_output("{}\n{}".format(game.world_map.to_json(), game.world_map.to_ascii()))
        return "Sent Gamestart to people"


class ClientConnect:

    def __init__(self, websocket):
        self.ws = websocket
        self.incoming = asyncio.Queue()
        self.outgoing = asyncio.Queue()

    def manual_output(self, message):
        self.outgoing.put_nowait(message)

    @asyncio.coroutine
    def get_message(self):
        msg_in = yield from self.ws.recv()
        logging.info("Client sent message: {}".format(msg_in))
        yield from self.incoming.put(msg_in)

    @asyncio.coroutine
    def parse_incoming(self, server):
        msg_to_consume = yield from self.incoming.get()
        msg_to_consume = server.message_handler(msg_to_consume, self)
        if msg_to_consume:
            yield from self.outgoing.put(msg_to_consume)

    @asyncio.coroutine
    def send_message(self, message):
        logging.info("Sending message: {}".format(message))
        yield from self.ws.send(message)

    @asyncio.coroutine
    def prepare_send(self):
        msg_out = yield from self.outgoing.get()
        return msg_out
