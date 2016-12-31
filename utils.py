def direction_as_movement_delta(direction):
    directions = {"DOWN"  : (0, 1),
            "UP"    : (0, -1),
            "RIGHT" : (1, 0),
            "LEFT"  : (-1, 0),
            "STAY"  : (0, 0)
        }

    return directions[direction.upper()]
