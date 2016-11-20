#!/usr/bin/env python

import asyncio
import websockets
import sys

@asyncio.coroutine
def hello():
    websocket = yield from websockets.connect('ws://localhost:1234/training')

    while True:
        try:
            name = input("> ")
            if name == "quit" or name == "exit":
                break
            elif name == "reg":
                yield from websocket.send('{"type" : "register", "name" : "legget"} ')
            elif name == "start":
                yield from websocket.send('{"type" : "start_game", "name" : "legget"}')
            else:
                yield from websocket.send(name)

            greeting = yield from websocket.recv()
            print("< {}".format(greeting))
        except:
            pass


asyncio.get_event_loop().run_until_complete(hello())
