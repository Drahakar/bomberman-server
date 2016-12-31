from .powerup import Powerup

class ExtraBomb(Powerup):
    def __init__(self, coord):
        super().__init__(coord)

    def use(self, player):
        player.num_bombs += 1

