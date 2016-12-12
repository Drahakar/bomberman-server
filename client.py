#!/usr/bin/env python

from websocket import create_connection
import sys
from threading import Thread
from json import dumps


def receive():
    while True:
        try:
            greeting = ws.recv()
            print("< {}".format(greeting))
        except:
            pass

ws = create_connection('ws://localhost:1234/training')

receiver = Thread(target=receive)
receiver.setDaemon(True)
receiver.start()

while True:
    name = input("> ")
    if name == "quit" or name == "exit":
        break
    if name == "reg":
        ws.send('{"type" : "register", "name" : "legget"} ')
    elif name == "start":
        ws.send('{"type" : "start_game", "name" : "legget"}')
    elif name == "con":
        ws = create_connection('ws://localhost:1234/training')
    elif name.startswith("m"):
        to_send = {'type' : 'move', 'direction' : name[1:], 'plant_bomb' : False}
        ws.send(dumps(to_send))
