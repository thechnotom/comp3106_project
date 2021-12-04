# Resources on the board (food, shelter)

from Element import Element

class Resource (Element):

    def __init__ (self, identifier, init_loc, effects):
        super().__init__(identifier, init_loc)
        self._effects = effects

    def get_effects (self): return self._effects