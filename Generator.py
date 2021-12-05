# Manages generation of board elements

from utilities import ElementType
from Creature import Creature
from Food import Food
from Obstacle import Obstacle
from Shelter import Shelter

class Generator:

    def __init__ (self):
        self.__count = {
            ElementType.CREATURE : {},
            ElementType.FOOD : 0,
            ElementType.SHELTER : 0,
            ElementType.OBSTACLE : 0
        }

    def creature (self, elements, init_loc, species):
        if (species.get_name() not in self.__count[ElementType.CREATURE]):
            self.__count[ElementType.CREATURE][species.get_name()] = 0
        self.__count[ElementType.CREATURE][species.get_name()] += 1
        return Creature(elements, self.__count[ElementType.CREATURE][species.get_name()], self, init_loc, species)

    def food (self, init_loc, restoration):
        self.__count[ElementType.FOOD] += 1
        return Food(self.__count[ElementType.FOOD], init_loc, restoration)

    def shelter (self, init_loc, restoration):
        self.__count[ElementType.SHELTER] += 1
        return Shelter(self.__count[ElementType.SHELTER], init_loc, restoration)

    def obstacle (self, init_loc, cost):
        self.__count[ElementType.OBSTACLE] += 1
        return Obstacle(self.__count[ElementType.OBSTACLE], init_loc, cost)