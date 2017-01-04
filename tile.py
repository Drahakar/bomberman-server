from powerups import Powerup
class Tile:
    def __init__(self, content=None):
        self.content = set()
        if content:
            self.content.add(content)

    def content_classes(self):
        return [x.__class__ if not isinstance(x, Powerup) else Powerup for x in self.content]

    def add(self, elem):
        self.content.add(elem)

    def remove(self, elem):
        self.content.remove(elem)
