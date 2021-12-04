# Food class

from Resource import Resource

class Food (Resource):

    def __init__ (self, identifier, init_loc, restoration):
        super().__init__(identifier, init_loc, {"restoration" : restoration})

    def get_restoration (self):
        return self.get_effects()["restoration"]

    def __hash__ (self):
        return sum(self._location.get_coords()) + self._effects["restoration"]

    def __eq__ (self, other):
        return self._location.get_coords() == other.get_location().get_coords() and self._effects["restoration"] == other.get_effects()["restoration"]