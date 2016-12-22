import asyncio
import websockets
import argparse
import logging
from server import Server

def main():
    parser = argparse.ArgumentParser(description="Bomberman websocket server")
    parser.add_argument("listen_host", help="Hosts to listen to.")
    parser.add_argument("listen_port", help="Port to listen to.", type=int)
    parser.add_argument("-l", "--log", dest="loglevel",  help="Loglevel. DEBUG|INFO|WARNING|ERROR|CRITICAL", default="INFO")
    args = parser.parse_args()

    bomb_server = Server(args.loglevel, args.listen_host, args.listen_port)
    bomb_server.start()


if __name__=="__main__":
    main()
