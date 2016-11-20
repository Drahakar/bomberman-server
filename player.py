from uuid import uuid4

class Player:
    def __init__(self, name):
        self.name = name
        self.p_id = str(uuid4())
        self.coordinate = None
        self.alive = False

    def __str__(self):
        return "Name: {}, id: {}".format(self.name, self.p_id)

    def __repr__(self):
        return "Name: {}, id: {}".format(self.name, self.p_id)
