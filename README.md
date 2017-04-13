# Websocket Bomberman server

A websocket bomberman server written in python 3 with asyncio and websockets.

## Setup:

### Database:

```
python3 setup.py
```

### Server requirements:
```
pip3 install -r requirements-server.txt
```

### Test-client requirements:
```
pip3 install -r requirements-client.txt
```

### Running
```
python3 main.py <LISTEN-HOST> <PORT>
```

## Commands

The server communicates over websockets via json. These are the valid commands:

### Register
```
{"command" : "register", "name" : <YOUR NAME>}
```
Register your client for a game. A client must register in order to be able to play games.

### Start a game
```
{"command" : "start"}
```
This command can only be invoked by players who are registered for a game. This will
start a game with all registered players.

### Move player
```
{"command" : "move", "direction" : <DIRECTION>, "plant_bomb" : <BOOLEAN>}
```
Each tick for the server a player can make a move. 

Valid **directions** are:
* UP
* DOWN
* LEFT
* RIGHT
* STAY

Valid **plant_bomb** values are:
* true
* false

If a player omits "plant_bomb" or the player doesn't have any bombs left, this will
default to false.

## Frontend commands

### Get all states for an old game
```
{"command" : "old_game", "id" : <NUMBER>}
```
