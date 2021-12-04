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
            ElementType.DEAD : set(),
            ElementType.NEW : set()
        }
        self.__generator = Generator()
        self.__step = 0
        self.__population_record = {}
        self.__species_update_steps = {}  # tracks the last step a species count was modified
    
    def get_step (self): return self.__step
    def get_population_record (self): return self.__population_record

    def adjust_species_count (self, species, operation):
        if (species not in self.__species_update_steps):
            self.__species_update_steps[species] = 0

        if (self.__step not in self.__population_record):
            self.__population_record[self.__step] = {}
        if (species not in self.__population_record[self.__step]):
            self.__population_record[self.__step][species] = 0
        last_update_step = self.__species_update_steps[species]
        self.__population_record[self.__step][species] = operation(
            self.__population_record[last_update_step][species],
            1
        )
        self.__species_update_steps[species] = self.__step

    def increase_species_count (self, species):
        def add (val_1, val_2):
            return val_1 + val_2
        self.adjust_species_count(species, add)
    
    def decrease_species_count (self, species):
        def sub (val_1, val_2):
            return val_1 - val_2
        self.adjust_species_count(species, sub)

    def create_creature (self, init_loc, species):
        self.__elements[ElementType.CREATURE].add(self.__generator.creature(self.__elements, init_loc, species))
        self.increase_species_count(species.get_name())

    def create_food (self, init_loc, restoration):
        self.__elements[ElementType.FOOD].add(self.__generator.food(init_loc, restoration))

    def create_shelter (self, init_loc, restoration):
        self.__elements[ElementType.SHELTER].add(self.__generator.shelter(init_loc, restoration))

    def remove_dead (self):
        for element in self.__elements[ElementType.DEAD]:
            if (isinstance(element, Creature)):
                self.__elements[ElementType.CREATURE].remove(element)
                self.decrease_species_count(element.get_species())
        self.__elements[ElementType.DEAD].clear()

    def add_new (self):
        for element in self.__elements[ElementType.NEW]:
            if (isinstance(element, Creature)):
                self.__elements[ElementType.CREATURE].add(element)
                self.increase_species_count(element.get_species())
        self.__elements[ElementType.NEW].clear()

    def advance (self):
        print_d("Begining creature advancements", "board_adv")
        for creature in self.__elements[ElementType.CREATURE]:
            print_d(f"Creature advancing: {creature}", "board_adv")
            creature.advance()
        self.remove_dead()
        self.add_new()
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

    def update_population_record (self):
        self.__population_record[self.__step] = {}
        curr_record = self.__generator.get_creature_counts()
        for species in curr_record:
            # don't just want a reference to the dictionary
            self.__population_record[self.__step][species] = curr_record[species]

    def creature_status_string (self):
        result = "--- Status ---\n"
        for creature in self.__elements[ElementType.CREATURE]:
            result += f"Creature ({creature.get_quick_label()}): {creature.health_string()}, Restlessness: {creature.get_restlessness()}, "
            result += f"Food: {creature.get_food_amount()}, Goal: {creature.get_goal()}\n"
        return result

    def population_record_string (self):
        result = "=== Population Record ===\n"
        for step in self.__population_record:
            result += f"Step {step}:\n"
            for species in self.__population_record[step]:
                result += f"    {species}: {self.__population_record[step][species]}\n"
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
                    result += str(element.get_species())[0].upper()
                elif (isinstance(element, Food)):
                    result += "f"
                elif (isinstance(element, Shelter)):
                    result += "s"
                else:
                    result += "?"
                result += " "
            result += "\n"
        return result