# place where creatures can regenerate health and reproduce

from utilities import print_d
from Element import Element
from Resource import Resource

class Shelter (Resource):

    def __init__ (self, identifier, init_loc, restoration=1):
        super().__init__(identifier, init_loc, {"restoration" : restoration})

    def get_restoration (self):
        return self.get_effects()["restoration"]

    def __hash__ (self):
        return sum(self._location.get_coords()) + self._effects["restoration"]