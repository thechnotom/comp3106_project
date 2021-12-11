# Storage and management of elements being simulated

from utilities import print_d, elements_at, ElementType, element_dict_to_set, get_location_dictionary
from utilities import elements_at_location, import_csv, import_json
from Generator import Generator
from Creature import Creature
from Location import Location
from Food import Food
from Shelter import Shelter
from Species import Species
from Obstacle import Obstacle
import random

class Board:

    # constructor
    # top_left: Location instance at the top-left of the area where food should generate
    # bottom_right: Location instance at the bottom-right of the area where food should generate
    # config_filename: name of the configuration JSON file
    def __init__ (self, top_left, bottom_right, config_filename):
        self.__config = import_json(config_filename)
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
        self.__food_record = {}
        self.__species_update_steps = {}  # tracks the last step a species count was modified
        self.__limits = [top_left, bottom_right]  # Location instances specifying the corners of the area

    # create the board from a CSV layout
    # layout_filename: name of the CSV file containing the layout
    # config_filename: name of the configuration JSON file
    @classmethod
    def from_csv (cls, layout_filename, config_filename):
        raw_data = import_csv(layout_filename)
        board = cls(
            Location([0, 0]),
            Location([len(raw_data), len(raw_data[0])]),
            config_filename
        )
        for row in range(0, len(raw_data)):
            for col in range(0, len(raw_data[row])):
                curr_label = raw_data[row][col]
                if (curr_label == board.__config["config"]["csv_labels"]["empty"]):
                    continue
                curr_loc = Location([row, col])
                if (curr_label == board.__config["config"]["csv_labels"]["shelter"]):
                    board.create_shelter(curr_loc, random.randint(
                        board.__config["config"]["random"]["shelter"]["restoration"]["min"],
                        board.__config["config"]["random"]["shelter"]["restoration"]["max"]
                    ))
                elif (curr_label == board.__config["config"]["csv_labels"]["food"]):
                    board.generate_food(
                        1,
                        1,
                        board.__config["config"]["random"]["food"]["restoration"]["min"],
                        board.__config["config"]["random"]["food"]["restoration"]["max"],
                        curr_loc
                    )
                elif (curr_label == board.__config["config"]["csv_labels"]["obstacle"]["passable"]):
                    board.create_obstacle(
                        curr_loc,
                        random.randint(
                            board.__config["config"]["random"]["obstacle"]["cost"]["min"],
                            board.__config["config"]["random"]["obstacle"]["cost"]["max"]
                        )
                    )
                elif (curr_label == board.__config["config"]["csv_labels"]["obstacle"]["impassable"]):
                    board.create_obstacle(curr_loc, float("inf"))
                else:
                    if (curr_label in board.__config["species"]):
                        board.create_creature(curr_loc, board.build_species(curr_label))
                    else:
                        print_d(f"Unable to find species: {curr_label}", "board_csv")
        return board

    # getters
    def get_step (self): return self.__step
    def get_population_record (self): return self.__population_record
    def get_limits (self): return self.__limits
    def get_food_record (self): return self.__food_record

    def get_origin_coords (self):
        return self.__limits[0].get_coords()

    def get_board_dimensions (self):
        return [
            self.__limits[1].get_coords()[0] - self.__limits[0].get_coords()[0],
            self.__limits[1].get_coords()[1] - self.__limits[0].get_coords()[1]
        ]

    def get_all_elements (self):
        return set.union(
            self.__elements[ElementType.CREATURE],
            self.__elements[ElementType.FOOD],
            self.__elements[ElementType.SHELTER],
            self.__elements[ElementType.OBSTACLE]
        )

    # update the count for a species
    # species: name of species being updated
    # operation: add or subtract function taking two arguments
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

    # increase the count for a species
    # species: name of the species being updated
    def increase_species_count (self, species):
        def add (val_1, val_2):
            return val_1 + val_2
        self.adjust_species_count(species, add)
    
    # decrease the count for a species
    # species: name of the species being updated
    def decrease_species_count (self, species):
        def sub (val_1, val_2):
            return val_1 - val_2
        self.adjust_species_count(species, sub)

    # create a creature
    # init_loc: initial location of the creature
    # species: Species instance representing the creature's species
    def create_creature (self, init_loc, species):
        self.__elements[ElementType.CREATURE].add(self.__generator.creature(self.__elements, init_loc, species))
        self.increase_species_count(species.get_name())

    # create food
    # init_loc: initial location of the food
    # restoration: the amount of health the food recovers upon consumption
    def create_food (self, init_loc, restoration):
        self.__elements[ElementType.FOOD].add(self.__generator.food(init_loc, restoration))

    # create shelter
    # init_loc: location of the shelter
    # restoration: the amount of health the shelter recovers for any creatures at its location every step
    def create_shelter (self, init_loc, restoration):
        self.__elements[ElementType.SHELTER].add(self.__generator.shelter(init_loc, restoration))

    # create an obstacle
    #
    def create_obstacle (self, init_loc, cost):
        self.__elements[ElementType.OBSTACLE].add(self.__generator.obstacle(init_loc, cost))

    def build_species (self, name):
        return Species(
            name,
            health=self.__config["species"][name]["health"],
            speed=self.__config["species"][name]["speed"],
            vulnerability=self.__config["species"][name]["vulnerability"],
            sight=self.__config["species"][name]["sight"],
            resourcefulness=self.__config["species"][name]["resourcefulness"]
        )

    def get_empty_location (self, attempts=10):
        # don't want to use elements_at since that would have to be repeated every loop
        location_dict = get_location_dictionary(self.get_all_elements())
        for i in range(0, attempts):
            location = Location([
                random.randint(
                    self.__limits[0].get_coords()[0],
                    self.__limits[1].get_coords()[0]
                ),
                random.randint(
                    self.__limits[0].get_coords()[1],
                    self.__limits[1].get_coords()[1]
                )
            ])
            if (elements_at_location(location_dict, location) is None):
                return location
        print_d(f"Could not find valid location after {attempts} attempts", "board_generation")
        return None

    def generate_food (self, tries, chance, min_rest, max_rest, location=None):
        limit = self.__config["config"]["limits"]["food"]["amount"]
        for i in range(0, tries):
            if (limit >= 0 and len(self.__elements[ElementType.FOOD]) >= limit):
                return
            if (random.random() <= chance):
                if (location is None):
                    location = self.get_empty_location()
                if (location is not None):
                    self.create_food(location, random.randint(min_rest, max_rest))

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
        self.generate_food(
            self.__config["config"]["limits"]["food"]["tries"],
            self.__config["config"]["random"]["food"]["chance"],
            self.__config["config"]["random"]["food"]["restoration"]["min"],
            self.__config["config"]["random"]["food"]["restoration"]["max"]
        )
        print_d("Completed creature advancements", "board_adv")
        self.__food_record[self.__step] = len(self.__elements[ElementType.FOOD])
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
            result += f"Food: {creature.get_food_amount()}, Location: {creature.get_location()}, Goal: {creature.goal_string()}\n"
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
                    result += self.__config["config"]["csv_labels"]["empty"]
                elif (isinstance(element, Creature)):
                    result += str(element.get_species())[0].upper()
                elif (isinstance(element, Food)):
                    result += self.__config["config"]["csv_labels"]["food"]
                elif (isinstance(element, Shelter)):
                    result += self.__config["config"]["csv_labels"]["shelter"]
                elif (isinstance(element, Obstacle)):
                    if (element.is_passable()):
                        result += self.__config["config"]["csv_labels"]["obstacle"]["passable"]
                    else:
                        result += self.__config["config"]["csv_labels"]["obstacle"]["impassable"]
                else:
                    result += "?"
                result += " "
            result += "\n"
        return result