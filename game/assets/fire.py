from game import config


class FireEvent:
    BURN_OUT, BURNING = range(2)


class Fire:
    def __init__(self, owner, coords, duration=config.FIRE_DURATION):
        self.owner = owner
        self.coords = coords
        self.duration = duration

    def tick(self):
        self.duration -= 1
        if self.duration:
            return FireEvent.BURNING
        else:
            return FireEvent.BURN_OUT

    def ascii(self):
        return "f"
