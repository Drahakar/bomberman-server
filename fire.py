from fire_event import FireEvent

class Fire:
    def __init__(self, fire_id, owner, coords, duration=3):
        self.fire_id = fire_id
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
