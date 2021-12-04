# Represents an element's location on the board

from utilities import print_d
from math import sqrt

class Location:

    def __init__ (self, coords=[None, None]):
        self.__coords = coords

    @classmethod
    def from_xy (cls, x, y):
        return cls([x, y])
    
    def copy (self):
        return Location(list(self.__coords))

    # Getters
    def get_coords (self): return self.__coords
    def get_x (self): return self.__coords[0]
    def get_y (self): return self.__coords[1]

    # Dimension of the location
    def get_dim (self):
        return len(self.__coords)

    # Euclidean distance from another Location
    def eucl_dist (self, loc):
        if (self.get_dim() != loc.get_dim()):
            print_d("Location dimensions must match (eucl)")
            return -1
        result = 0
        for i in range(0, self.get_dim()):
            result += (self.__coords[i] - loc.get_coords()[i]) ** 2
        return sqrt(result)

    # Manhattan distance from another location
    def manh_dist (self, loc):
        if (self.get_dim() != loc.get_dim()):
            print_d("Location dimensions must match (manh)")
            return -1
        result = 0
        for i in range(0, self.get_dim()):
            result += abs(self.__coords[i] - loc.get_coords()[i])
        return result

    def __hash__ (self):
        return sum(self.__coords)

    def __eq__ (self, other):
        return self.__coords == other.get_coords()

    def __str__ (self):
        return str(self.__coords)