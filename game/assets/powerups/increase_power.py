from .powerup import Powerup


class IncreasePower(Powerup):
    def __init__(self, coord):
        super().__init__(coord)

    def use(self, player):
        player.power += 1

