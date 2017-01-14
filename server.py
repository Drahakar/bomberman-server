from database import Database
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
        self.registered_clients = {}
        self.client_to_game = {}
        logging.basicConfig(format="%(asctime)s %(levelname)s  %(message)s", level=loglevel)
        self.types = {
            "register" : self.register_player,
            "start_game" : self.start_game,
            "move" : self.register_move,
            "old_game" : self.get_old_game,
        }

    def start(self):
        logging.info("Starting server. Listening on {}:{}".format(self.host, self.port))
        start_server = websockets.serve(self.request_handler, self.host, self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    @asyncio.coroutine
    def request_handler(self, websocket, path):
        client = ClientConnect(self, websocket)
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
                self.server.remove(self)

    def remove_client(self, client):
        self.clients.remove(client)
        if client in self.registered_clients:
            del(self.registered_clients[client])
        logging.info("Removed connection. Current connections: {}".format(len(self.clients)))

    def time_handler(self, response_time, websocket):
        return response_time > 3 and websocket in self.client_to_game

    def message_handler(self, message, client):
        try: 
            message = json.loads(message)
            return self.types[message["type"]](message, client)
        except (ValueError, KeyError) as e:
            logging.debug(traceback.print_exc())
            return self.send_reply(client, "error", "Invalid request.")

    def register_player(self, message, client):
        if client in self.registered_clients:
            return self.send_reply(client, "error", "Player already registered")
        else:
            self.registered_clients[client] = Player(message["name"])
            logging.info("Registered players: {}".format(self.registered_clients))
            return self.send_reply(client, "info", "You are now registered. Waiting for game...")

    def register_move(self, message, client):
        if client not in self.client_to_game:
            return self.send_reply(client, "error", "You are not in a game")
        current_player = self.registered_clients[client]
        current_game = self.client_to_game[client]
        try:
            if current_player in current_game.world_map.players:
                current_game.get_player_move(client, (message["direction"], message["plant_bomb"]))
            else:
                return self.send_reply(client, "game_over", "You are dead, you have to wait for the game to finish.")

        except KeyError:
            pass
        current_game.tick_handler()
        if current_game.ended:
            self.end_game(current_game)

    def start_game(self, message, start_client):
        game = Game(self.registered_clients, 0)
        logging.info("Starting game")
        for client in self.registered_clients:
            self.client_to_game[client] = game
        for client in self.registered_clients:
            client.manual_output("{}\n{}".format(
                game.world_map.to_json(),
                game.world_map.to_ascii()
            ))

    def end_game(self, game):
        for client in list(game.players):
            del(self.registered_clients[client])
            del(self.client_to_game[client])
        Database.insert_game_states(json.dumps(game.states))

    def get_old_game(self, message, client):
        try:
            game = Database.get_game(message['id'])
        except KeyError:
            return self.send_reply(client, "error", "'id'-parameter is missing")

        if game:
            self.send_reply(client, "info", game)
        else:
            self.send_reply(client, "error", "Game id doesn't exist")

    def send_reply(self, client, event, text):
        client.manual_output(json.dumps({'event' : event, 'text' : text}))


class ClientConnect:

    def __init__(self, server, websocket):
        self.server = server
        self.ws = websocket
        self.incoming = asyncio.Queue()
        self.outgoing = asyncio.Queue()

    def manual_output(self, message):
        self.outgoing.put_nowait(message)

    @asyncio.coroutine
    def get_message(self):
        try:
            msg_in = yield from self.ws.recv()
        except ConnectionClosed:
            self.server.remove_client(self)
            return
        logging.info("Client sent message: {}".format(msg_in))
        yield from self.incoming.put(msg_in)

    @asyncio.coroutine
    def parse_incoming(self, server):
        msg_to_consume = yield from self.incoming.get()
        server.message_handler(msg_to_consume, self)

    @asyncio.coroutine
    def send_message(self, message):
        logging.info("Sending message: {}".format(message))
        yield from self.ws.send(message)

    @asyncio.coroutine
    def prepare_send(self):
        msg_out = yield from self.outgoing.get()
        return msg_out
