import abc

from enums import Positions


class Event(abc.ABC):
    def resolve(self):
        raise NotImplemented

class Single(Event):
    def resolve(self, game):
        game.single()

class Double(Event):
    def resolve(self, game):
        game.double()

class HomeRun(Event):
    def resolve(self, game):
        game.home_run()

class DefChance(Event):
    def __init__(self, pos: Positions):
        self.pos = pos

    def resolve(self, game):
        # roll on def table
        raise NotImplemented

class RunnersAdvance(Event):
    def __init__(self, n: int):
        self.n = n

    def resolve(self, game):
        # advance runners
        raise NotImplemented
