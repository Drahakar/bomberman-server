import sqlite3
import json

class Database:
    # Use static variables for connection and cursor to only have one constant connection to the database.
    conn = sqlite3.connect('saved_games.db')
    c = conn.cursor()

    @staticmethod
    def create():
        Database.c.execute('CREATE TABLE games (id INTEGER PRIMARY KEY AUTOINCREMENT, game text)')

    @staticmethod
    def get_game(game_id):
        # Ensure that it is an int.
        try:
            game_id = int(game_id)
        except ValueError:
            return

        Database.c.execute('SELECT game from games where id=?', (game_id,))
        result = Database.c.fetchone()
        if result:
            return json.loads(result[0])

    @staticmethod
    def get_all_games():
        Database.c.execute('SELECT * from games')
        return Database.c.fetchall()

    @staticmethod
    def insert_game_states(states):
        Database.c.execute('INSERT INTO games(game) VALUES(?)', (states,))
        Database.conn.commit()
