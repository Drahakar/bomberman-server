#!/usr/bin/env python

from json import dumps
from threading import Thread
from websocket import create_connection

QUIT_COMMAND = "quit"
REGISTER_COMMAND = "reg"
START_COMMAND = "start"
CONNECT_COMMAND = "con"
MOVE_COMMAND = "m"


def receive():
    while True:
        try:
            greeting = ws.recv()
            print("< {}".format(greeting))
        except:
            pass


ws = create_connection('ws://localhost:8080/training')

receiver = Thread(target=receive)
receiver.setDaemon(True)
receiver.start()

while True:
    name = input("> ")
    if name == QUIT_COMMAND:
        break
    if name.startswith(REGISTER_COMMAND):
        to_send = {'type': 'register', 'name': name[len(REGISTER_COMMAND):]}
        ws.send(dumps(to_send))
    elif name.startswith(START_COMMAND):
        to_send = {'type': 'start_game', 'name': name[len(START_COMMAND):]}
        ws.send(dumps(to_send))
    elif name == CONNECT_COMMAND:
        ws = create_connection('ws://localhost:1234/training')
    elif name.startswith(MOVE_COMMAND):
        args = name.split(" ")
        bomb = len(args) > 2
        to_send = {'type': 'move', 'direction': args[1], 'plant_bomb': bomb}
        ws.send(dumps(to_send))
