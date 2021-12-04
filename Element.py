# Top-level object that items on the board inherit from

from Location import Location

class Element:

    def __init__ (self, identifier, init_loc):
        self._id = identifier
        if (isinstance(init_loc, Location)):
            self._location = init_loc
        elif (isinstance(init_loc, list)):
            self._location = Location(init_loc)
        else:
            raise TypeError

    def get_id (self): return self._id
    def get_location (self): return self._location
    def set_location (self, loc): self._location = loc

    def distance (self, element):
        return self._location.manh_dist(element.get_location())

    def __hash__ (self):
        return NotImplemented

    def __eq__ (self, other):
        return NotImplemented

    def __str__ (self):
        return f"Element at {self._location}"