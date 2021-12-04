# An item that impedes (but does not prevent) travel

from Element import Element

class Obstacle (Element):

    def __init__ (self, identifier, init_loc, cost, passable=True):
        super().__init__(identifier, init_loc)
        self.__cost = cost
        self.__passable = passable

    def get_cost (self): return self.__cost
    def is_passable (self): return self.__passable