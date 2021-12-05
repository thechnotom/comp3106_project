# Utility functions that can be used in multiple classes

from enum import Enum
import csv
import json

# goals that a creature can have
class Goal (Enum):
    FOOD = 1
    SHELTER = 2
    REPRODUCE = 3
    WAIT = 4
    HEAL = 5
    WANDER = 6

# the types of elements
class ElementType (Enum):
    CREATURE = 1
    FOOD = 2
    SHELTER = 3
    OBSTACLE = 4
    DEAD = 5
    NEW = 6

# the directions that a creature can move
def get_movement_modifiers ():
    return [[0, 1], [1, 0], [0, -1], [-1, 0]]

# add two lists element-wise
def list_addition (list_1, list_2):
    if (len(list_1) != len(list_2)):
        raise Exception("Lists must be of equal length for list addition")
    result = []
    for i in range(0, len(list_1)):
        result.append(list_1[i] + list_2[i])
    return result

# Debug print
def print_d (string, tag="default"):
    # which print_d calls should be displayed
    # default, path, board_adv, creature_adv, creature_move, creature_path, creature_nearest, creature_goal_valid, board_generation, board_csv
    allowed_tags = []
    if (tag in allowed_tags):
        print(f"DEBUG: {string}")

# get the elements at a specific location
# loc_dict: dictionary of locations and elements (likely from get_location_dictionary)
# loc: location being checked
def elements_at_location (loc_dict, loc):
    try:
        return loc_dict[loc]
    except KeyError:
        return None

# dictionary with location as key and element as value
# elements: iterable of elements
def get_location_dictionary (elements):
    result = {}
    for element in elements:
        loc = element.get_location()
        if (loc in result):
            result[loc].append(element)
        else:
            result[loc] = [element]
    return result

# combine elements_at_location and get_location_dictionary
# elements: iterable of elements
# loc: location being checked
def elements_at (elements, loc):
    return elements_at_location(get_location_dictionary(elements), loc)

# import a CSV file
# filename: name of CSV file
def import_csv (filename):
    result = []
    with open(filename, "r") as f:
        reader = csv.reader(f, delimiter=",")
        for line in reader:
            result.append(line)
    return result

# import a JSON file
# filename: name of JSON file
def import_json (filename):
    raw_data = None
    with open(filename, "r") as f:
        raw_data = f.read()
    return json.loads(raw_data)

# basic (and slightly modified) implementation of a stack
class Stack:

    def __init__ (self):
        self.__values = []

    def get_list (self):
        return self.__values

    def push (self, value):
        self.__values.append(value)

    def pop (self):
        if (len(self.__values) > 0):
            return self.__values.pop()
        return None

    def peek (self):
        if (len(self.__values) > 0):
            return self.__values[-1]
        return None
    
    def peek_deep (self):
        if (len(self.__values) > 1):
            return self.__values[-2]
        return None

    def clear (self):
        self.__values.clear()

    def __len__ (self):
        return len(self.__values)

    def __str__ (self):
        return str(self.__values)

# takes a dictionary of sets containing elements and returns a single set of elements
# elements: dictionary of sets of elements (likely Board.__elements)
def element_dict_to_set (elements):
    result = set()
    for key in elements:
        result = set.union(result, elements[key])
    return result