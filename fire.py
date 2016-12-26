from fire_event import FireEvent

class Fire:
    def __init__(self, fire_id, owner, coords, duration=3):
        self.fire_id = fire_id
        self.owner = owner
        self.coords = coords
        self.duration = duration

    def tick(self, game_map, event=None):
        self.duration -= 1
        # Check if alive or not
        if self.duration:
            return FireEvent.BURNING
        else:
            del(game_map.fires[self.fire_id])
            return FireEvent.BURN_OUT
