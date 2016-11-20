import asyncio
import websockets
import argparse
import logging
from server import Server

@asyncio.coroutine
def hello(websocket, path):
    name = yield from websocket.recv()
    print("NAME RECIEVEVED")
    print("< {}".format(name))
    greeting = "LEGGET"
    yield from websocket.send(greeting)
    print("> {}".format(greeting))

def main():
    # import pdb; pdb.set_trace()
    # logger = logging.getLogger('websockets')
    # logger.setLevel(logging.INFO)
    # logger.addHandler(logging.StreamHandler())

    parser = argparse.ArgumentParser(description="Snakebot for cygni")
    parser.add_argument("-l", "--log", dest="loglevel",  help="Loglevel. DEBUG|INFO|WARNING|ERROR|CRITICAL", default="INFO")
    args = parser.parse_args()

    bomb_server = Server(args.loglevel, 'localhost', 1234)
    bomb_server.start()


if __name__=="__main__":
    main()
