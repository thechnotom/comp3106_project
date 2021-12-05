# An item that impedes (but does not prevent) travel

from Element import Element

class Obstacle (Element):

    def __init__ (self, identifier, init_loc, cost):
        super().__init__(identifier, init_loc)
        self.__cost = cost
        self.__passable = cost < float("inf")

    def get_cost (self): return self.__cost
    def is_passable (self): return self.__passable

    def __hash__ (self):
        return sum(self._location.get_coords())

    def __eq__ (self, other):
        return self._location.get_coords() == other.get_location().get_coords() and self.__passable == other.is_passable()