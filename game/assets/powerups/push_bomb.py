from .powerup import Powerup


class PushBomb(Powerup):
    def __init__(self, coord):
        super().__init__(coord)

    def use(self, player):
        player.can_push_bombs = True
