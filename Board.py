# Storage and management of elements being simulated

from utilities import print_d, elements_at, ElementType, element_dict_to_set
from Generator import Generator
from Creature import Creature
from Location import Location
from Food import Food
from Shelter import Shelter

class Board:

    def __init__ (self):
        self.__elements = {
            ElementType.CREATURE : set(),
            ElementType.FOOD : set(),
            ElementType.SHELTER : set(),
            ElementType.OBSTACLE : set(),
            ElementType.DEAD : set()
        }
        self.__generator = Generator()
        self.__step = 0
    
    def get_step (self): return self.__step

    def create_creature (self, init_loc, species):
        self.__elements[ElementType.CREATURE].add(self.__generator.creature(self.__elements, init_loc, species))

    def create_food (self, init_loc, restoration):
        self.__elements[ElementType.FOOD].add(self.__generator.food(init_loc, restoration))

    def create_shelter (self, init_loc, restoration):
        self.__elements[ElementType.SHELTER].add(self.__generator.shelter(init_loc, restoration))

    def remove_dead (self):
        for element in self.__elements[ElementType.DEAD]:
            if (isinstance(element, Creature)):
                self.__elements[ElementType.CREATURE].remove(element)
        self.__elements[ElementType.DEAD].clear()

    def advance (self):
        print_d("Begining creature advancements", "board_adv")
        for creature in self.__elements[ElementType.CREATURE]:
            print_d(f"Creature advancing: {creature}", "board_adv")
            creature.advance()
        self.remove_dead()
        print_d("Completed creature advancements", "board_adv")
        self.__step += 1

    def primary_element_at (self, elements, loc):
        options = elements_at(elements, loc)
        if (options is None):
            return None
        for element in options:
            if (isinstance(element, Creature)):
                return element
        return options[0]

    def creature_health_string (self):
        result = "--- Health ---\n"
        for creature in self.__elements[ElementType.CREATURE]:
            result += f"Creature ({creature.get_quick_label()}): {creature.health_string()}, Goals: {creature.get_all_goals()}\n"
        return result

    def get_board_string (self, base_coords, dim_limits):
        if (len(dim_limits) != 2):
            print_d(f"Cannot represent {len(dim_limits)} dimensions as string")
        if (len(dim_limits) != len(base_coords)):
            print_d("Number of dimensions must match the number of base coordinates")

        all_elements = element_dict_to_set(self.__elements)

        result = ""
        for row in range(base_coords[0], base_coords[0] + dim_limits[0]):
            for col in range(base_coords[0], base_coords[0] + dim_limits[1]):
                element = self.primary_element_at(all_elements, Location.from_xy(row, col))
                if (element is None):
                    result += "-"
                elif (isinstance(element, Creature)):
                    result += str(element.get_species())[0]
                elif (isinstance(element, Food)):
                    result += "f"
                elif (isinstance(element, Shelter)):
                    result += "s"
                else:
                    result += "?"
                result += " "
            result += "\n"
        return result