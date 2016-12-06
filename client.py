#!/usr/bin/env python

import asyncio
import websockets
import sys
from time import sleep

@asyncio.coroutine
def hello():

    while True:
            websocket = None
        try:
            websocket = yield from websockets.connect('ws://localhost:1234/training')
            yield from websocket.send('{"type" : "register", "name" : "legget"} ')
            greeting = yield from websocket.recv()
            print("< {}".format(greeting))
            sleep(1)

            yield from websocket.send('{"type" : "start_game", "name" : "legget"}')
            greeting = yield from websocket.recv()
            print("< {}".format(greeting))
            sleep(1)

            for i in range(2):
                yield from websocket.send('{"type" : "move", "direction" : "RIGHT", "plant_bomb" : false }')
                greeting = yield from websocket.recv()
                print("< {}".format(greeting))
                sleep(1)

            yield from websocket.send('{"type" : "move", "direction" : "DOWN", "plant_bomb" : false }')
            greeting = yield from websocket.recv()
            print("< {}".format(greeting))
            sleep(1)


            yield from websocket.send('{"type" : "move", "direction" : "DOWN", "plant_bomb" : true }')
            greeting = yield from websocket.recv()
            print("< {}".format(greeting))
            sleep(1)

            for i in range(7):
                yield from websocket.send('{"type" : "move", "direction" : "DOWN", "plant_bomb" : false }')
                greeting = yield from websocket.recv()
                print("< {}".format(greeting))
                sleep(1)


            yield from websocket.close()
            sleep(5)
        except:
            if websocket:
                yield from websocket.close()

    # while True:
        # try:
            # name = input("> ")
            # if name == "quit" or name == "exit":
                # break
            # elif name == "reg":
                # yield from websocket.send('{"type" : "register", "name" : "legget"} ')
            # elif name == "start":
                # yield from websocket.send('{"type" : "start_game", "name" : "legget"}')
            # else:
                # yield from websocket.send(name)

            # greeting = yield from websocket.recv()
            # print("< {}".format(greeting))
        # except:
            # pass


asyncio.get_event_loop().run_until_complete(hello())
