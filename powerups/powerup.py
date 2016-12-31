class Powerup:
    def __init__(self, coord):
        self.coord = coord

    def use(self, player):
        raise NotImplementedError

