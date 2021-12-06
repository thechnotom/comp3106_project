# An element that moves

from utilities import print_d, Goal, ElementType, elements_at, Stack, get_location_dictionary
from utilities import element_dict_to_set, get_movement_modifiers, list_addition
from Element import Element
from Food import Food
from Shelter import Shelter
from Path import Path
from Location import Location
from random import choice

class Creature (Element):

    # constructor
    # elements: dictionary of all elements (probably from Board)
    # identifier: value combined with the species name to form a unique identifier (probably from Generator)
    # generator: allows creatures to reproduce
    # init_loc: initial location of the creature
    # species: Species instance which details information about a creature's abilities
    def __init__ (self, elements, identifier, generator, init_loc, species):
        super().__init__(identifier, init_loc)
        self.__elements = elements  # set of all elements (needed to find/avoid food, shelter, and obstacles)
        self.__org_species = species  # needed to pass on to descendants
        self.__species = species.get_name()
        self.__set_attributes(species.get_attributes())
        self.__goal = Stack()  # indicates current objective (ex. food, reproduce, shelter)
        self.__path = None
        self.__food = []
        self.new_creature = generator.creature  # method to create new creatures
        self.__path_needed = False
        self.__curr_element = None
        self.__steps_waiting = 0
        self.__barred_shelters = set()
        self.__thresholds = {
            "shelter_healing" : 0.70,
            "restlessness" : 30,
            "heal_goal" : 0.20,
            "food_use" : 0.10
        }

    # getters
    def get_species (self): return self.__species
    def get_goal (self): return self.__goal.peek()
    def get_all_goals (self): return self.__goal
    def get_quick_label (self): return f"{self.__species}-{self._id}"
    def get_restlessness (self): return self.__steps_waiting
    def get_food_amount (self): return len(self.__food)

    # set attributes of creature (probably from a Species instance)
    # attributes: dictionary of attributes
    def __set_attributes (self, attributes):
        self.__health_max = attributes["health"]
        self.__health = attributes["health"]
        self.__speed = attributes["speed"]
        self.__vulnerability = attributes["vulnerability"]
        self.__sight = attributes["sight"]
        self.__resourcefulness = attributes["resourcefulness"]

    # get health as a percent
    def health (self):
        return self.__health / self.__health_max

    # add health to creature without going over maximum
    # amount: number of health points to add
    def add_health (self, amount):
        self.__health = min(self.__health + amount, self.__health_max)

    # remove health from creature without going below 0
    # amount: number of health points to remove
    def sub_health (self, amount):
        self.__health = max(self.__health - amount, 0)

    # determine if the creature is alive
    def is_alive (self):
        return self.__health > 0

    # add the creature to the list of dead elements (removal happens via Board)
    def die (self):
        # put in DEAD set for removal by Board
        self.__elements[ElementType.DEAD].add(self)

    # determine if a creature has at least a given amount of food
    def has_food (self, amount):
        return len(self.__food) >= amount

    # count steps taken waiting for partner for reproduction
    def restlessness (self):
        # if the creature is at a shelter or is desparate (need health), de-bar the shelters
        if (self.get_element_type(self.__curr_element) == ElementType.SHELTER or self.__goal.peek() == Goal.HEAL):
            self.__barred_shelters.clear()

        if (self.get_element_type(self.__curr_element) == ElementType.SHELTER):
            if (self.__steps_waiting > self.__thresholds["restlessness"]):
                self.__barred_shelters.add(self.__curr_element)
                if (self.__goal.peek() != Goal.SHELTER):
                    self.add_goal(Goal.SHELTER)
            else:
                if (self.health() >= self.__thresholds["shelter_healing"]):
                    self.__steps_waiting += 1
        else:
            self.__steps_waiting = 0

    # create another creature given specific conditions
    # generate_creature: whether or not the current creature is responsible for adding the new creature
    def reproduce (self, generate_creature=False):
        if (generate_creature):
            self.__elements[ElementType.NEW].add(self.new_creature(self.__elements, self._location.copy(), self.__org_species))
        self.achieve_goal()
        for i in range(0, self.__resourcefulness):
            self.__food.pop()

    # add a new goal to the stack
    # goal: goal to be added
    def add_goal (self, goal):
        print_d(f"goal added: {goal}", "creature_goal_change")
        self.__goal.push(goal)
        self.__path_needed = True

    # flag that the path must be recalculated
    def recalculate_goal (self):
        self.__path_needed = True

    # goal achieved and the path must be changed
    def achieve_goal (self):
        print_d(f"goal achieved: {self.__goal.peek()}", "creature_goal_change")
        self.__goal.pop()
        self.__path_needed = True

    # no need to change the path
    def pop_goal (self):
        self.__goal.pop()

    # determine if the creature is wandering for food
    def is_wandering_for_food (self):
        return self.__goal.peek() == Goal.WANDER and self.__goal.peek_deep() == Goal.FOOD

    # determine if the creature is wandering for shelter
    def is_wandering_for_shelter (self):
        return self.__goal.peek() == Goal.WANDER and self.__goal.peek_deep() == Goal.SHELTER

    # wether or not to consume a piece of food (food is required for reproduction but also staying alive)
    def food_decision (self):
        # is health is very low and creature has food, consume food
        if (self.health() < self.__thresholds["food_use"] and len(self.__food) > 0):
            self.add_health(self.__food.pop().get_restoration())

    # determine if the creatures current goal means the creature is walking
    def is_moving (self):
        if (self.__goal.peek() in [Goal.FOOD, Goal.SHELTER, Goal.WANDER, Goal.HEAL]):
            return True
        return False

    # update the goal
    def adjust_goal (self):
        # if there is no goal, try to reproduce
        if (self.__goal.peek() is None):
            self.add_goal(Goal.REPRODUCE)

        # if goal is to reproduce, there is enough food, and the creature is not at a shelter, go to shelter
        if (self.__goal.peek() == Goal.REPRODUCE and self.has_food(self.__resourcefulness) and self.get_element_type(self.__curr_element) != Goal.SHELTER):
            self.add_goal(Goal.SHELTER)

        # if the goal is to reproduce but the creature has insufficient food and sufficient health, get food
        if (self.__goal.peek() == Goal.REPRODUCE and not self.has_food(self.__resourcefulness) and self.health() > self.__thresholds["shelter_healing"]):
            for i in range(0, self.__resourcefulness - len(self.__food)):
                self.add_goal(Goal.FOOD)

        # if health gets too low and creature is moving, replace all goals with heal
        if (self.__goal.peek() != Goal.HEAL and self.__path is None and self.is_moving() and self.health() < self.__thresholds["heal_goal"]):
            self.__goal.clear()
            self.add_goal(Goal.REPRODUCE)
            self.add_goal(Goal.SHELTER)
            self.add_goal(Goal.HEAL)

        # goal is food or shelter but no food or shelter is in sight
        nearest_food = self.get_nearest_food()
        nearest_shelter = self.get_nearest_shelter(self.__barred_shelters)
        if ((self.__goal.peek() == Goal.FOOD and nearest_food is None) or (self.__goal.peek() == Goal.SHELTER and nearest_shelter is None)):
            self.add_goal(Goal.WANDER)

        # if we are wandering or looking for health and there is a path
        if ((self.__goal.peek() == Goal.WANDER or self.__goal.peek() == Goal.HEAL) and self.__path is not None):
            self.achieve_goal()

        if (self.__goal.peek() == Goal.SHELTER and self.get_element_type(self.__curr_element) == ElementType.SHELTER and len(self.__barred_shelters) == 0):
            self.achieve_goal()

    # preform the necessary action (ex. grab food from the environment, reproduce)
    def perform_action (self):
        element_type = self.get_element_type(self.__curr_element)

        # take food
        if (self.__goal.peek() == Goal.FOOD and element_type == ElementType.FOOD):
            self.__elements[ElementType.FOOD].remove(self.__curr_element)
            self.__food.append(self.__curr_element)
            self.__curr_element = None
            self.update_current_element()
            self.achieve_goal()

        # reproduce
        partner = self.reproduce_with()
        if (self.__goal.peek() == Goal.REPRODUCE and element_type == ElementType.SHELTER and partner is not None and self.has_food(self.__resourcefulness)):
            self.reproduce(generate_creature=True)
            self.achieve_goal()
            partner.reproduce(generate_creature=False)
            partner.achieve_goal()

        # at shelter (heal)
        if (element_type == ElementType.SHELTER):
            self.add_health(self.__curr_element.get_restoration())

        # decide whether food must be eaten
        self.food_decision()

    # check the goal to make sure it is still valid (ex. food still exists)
    def goal_valid (self):
        if (self.__goal.peek() == Goal.FOOD):
            if (self.__path is not None):
                if (self._location.eucl_dist(self.__path.get_goal()) > self.__sight):
                    print_d("valid - path exists but the food cannot be seen (assuming valid)", "creature_goal_valid")
                    return True
                if (not self.food_exists(self.__path.get_goal())):
                    print_d("invalid - path exists and there is no food at the goal", "creature_goal_valid")
                    return False  # path exists and there is not food at the goal
                print_d("valid - path exists and there is food at the goal", "creature_goal_valid")
                return True  # path exists and there is food at the goal
            print_d("invalid - there is no path", "creature_goal_valid")
            return False  # there is no path
        print_d("valid - the goal is not food", "creature_goal_valid")
        return True  # the goal is not food

    # determine if there is a creature that is not self at the location
    # loc: Location instance to check
    def creatures_at_location (self, loc):
        result = []
        for element in get_location_dictionary(self.__elements[ElementType.CREATURE])[loc]:
            if (isinstance(element, Creature) and element != self):
                result.append(element)
        return result

    # determine if there is a creature who can reproduce with the current creature at the current location (if yes, return it)
    def reproduce_with (self):
        creatures = self.creatures_at_location(self._location)
        for creature in creatures:
            if (self.get_species() == creature.get_species() and creature.has_food(self.__resourcefulness) and creature.get_goal() == Goal.REPRODUCE):
                return creature
        return None

    # element at current location (barring creatures)
    def current_location_element (self):
        for element in get_location_dictionary(element_dict_to_set(self.__elements))[self._location]:
            if (not isinstance(element, Creature)):
                return element
        return None

    # get the type (ElementType) of an element
    # element: element being tested
    def get_element_type (self, element):
        if (isinstance(element, Food)):
            return ElementType.FOOD
        if (isinstance(element, Shelter)):
            return ElementType.SHELTER
        return None

    # get the path to the next objective
    def prepare_goal (self):
        print_d(f"{self.get_quick_label()} attempting to get path with goal={self.__goal.peek()}", "creature_path")
        path = None
        nearest = None
        if (self.__goal.peek() == Goal.HEAL):
            print_d("getting path to nearest healing item", "creature_path")
            nearest_food = self.get_nearest_food()
            nearest_shelter = self.get_nearest_shelter()
            food_dist = float("inf")
            shelter_dist = float("inf")
            if (nearest_food is not None):
                food_dist = self._location.eucl_dist(nearest_food.get_location())
            if (nearest_shelter is not None):
                shelter_dist = self._location.eucl_dist(nearest_shelter.get_location())
            if (food_dist != float("inf") or shelter_dist != float("inf")):
                if (shelter_dist <= food_dist):
                    nearest = nearest_shelter
                else:
                    nearest = nearest_food
        elif (self.__goal.peek() == Goal.FOOD or self.is_wandering_for_food()):
            print_d("getting path to nearest food item", "creature_path")
            nearest = self.get_nearest_food()
        elif (self.__goal.peek() == Goal.SHELTER or self.__goal.peek() == Goal.REPRODUCE or self.is_wandering_for_shelter()):
            print_d("getting path to nearest shelter", "creature_path")
            nearest = self.get_nearest_shelter(self.__barred_shelters)
        print_d(f"nearest element found: {nearest}", "creature_path")
        if (nearest is None):
            self.__path = None
        else:
            path = Path(self._location, nearest.get_location(), self.__elements[ElementType.OBSTACLE], self.__sight)
            if (path.path_exists()):
                self.__path = path
            else:
                self.__path = None

    # verify that food exists at the given location
    # loc: Location instance being checked
    def food_exists (self, loc):
        elements = elements_at(self.__elements[ElementType.FOOD], loc)
        if (elements is None):
            return False
        if (len(elements) > 0):
            return True
        return False

    # move in the necessary manner (i.e., follow path or random walk)
    def move (self):
        print_d(f"{self.get_quick_label()} making movement", "creature_move")
        if (self.__path is not None):
            next_loc = self.__path.advance(self.__speed)
            if (next_loc is not None):
                print_d(f"{self.get_quick_label()} moving to {next_loc} from {self._location}", "creature_move")
                self.set_location(next_loc)
            else:
                self.goal = None

        if (self.__goal.peek() == Goal.WANDER or self.__goal.peek() == Goal.HEAL):
            next_loc = Location(list_addition(self._location.get_coords(), choice(get_movement_modifiers())))
            # we only need to check validity for wander/heal since Path takes care of it otherwise
            if (self.valid_move_location(next_loc)):
                self.set_location(next_loc)

        self.update_current_element()

    # updated the current element
    def update_current_element (self):
        self.__curr_element = self.current_location_element()

    # determine if the given location can be traversed to by the creature
    # loc: location being checked
    def valid_move_location (self, loc):
        elements = elements_at(self.__elements[ElementType.OBSTACLE], loc)
        if (elements is None):
            return True
        for element in elements:
            if (not element.is_passable()):
                return False
        return True

    # gets the nearest element to the creature
    # elements: iterable of elements
    def __get_nearest (self, elements, barring=set()):
        print_d(f"finding nearest element to {self._location} from {elements}", "creature_nearest")
        min_distance = float("inf")
        closest = None
        for element in elements:
            if (element in barring):
                continue
            distance = self._location.eucl_dist(element.get_location())
            print_d(f"distance to {element}: {distance} (sight={self.__sight})", "creature_nearest")
            if (distance < min_distance and distance <= self.__sight):
                min_distance = distance
                closest = element
        return closest

    # gets the nearest food to the creature
    def get_nearest_food (self):
        return self.__get_nearest(self.__elements[ElementType.FOOD])

    # gets the nearest shelter to the creature
    def get_nearest_shelter (self, barring=set()):
        return self.__get_nearest(self.__elements[ElementType.SHELTER], barring)

    # perform all updates to the creature for a single time step
    def advance (self):
        self.restlessness()
        self.adjust_goal()
        print_d(f"goal stack: {self.__goal}", "creature_adv")
        print_d(f"goal valid: {self.goal_valid()}, goal modified: {self.__path_needed}", "creature_adv")
        if (self.__path_needed or not self.goal_valid()):
            print_d("preparing goal", "creature_adv")
            self.prepare_goal()
        self.move()
        self.perform_action()
        if (self.get_element_type(self.__curr_element) != ElementType.SHELTER):
            self.sub_health(self.__vulnerability)
        if (not self.is_alive()):
            self.die()
        if (self.__path is not None):
            self.__path_needed = False

    # get a string representing the creature's health
    def health_string (self):
        return f"{self.__health}/{self.__health_max} ({int(round(self.health() * 100, 0))}%)"

    # get a string representing the creature's goals
    def goal_string (self):
        result = ""
        temp_goals = self.__goal.get_list()
        for i in range(0, len(temp_goals)):
            result += f"{temp_goals[i].name}"
            if (i < len(temp_goals) - 1):
                result += "->"
        return result

    def __hash__ (self):
        return self._id + hash(self.__species)

    def __eq__ (self, other):
        return self._id == other.get_id() and self.__species == other.get_species()

    def __str__ (self):
        return f"id={self._id}, species={self.__species}, health={self.__health}/{self.__health_max}, goal={self.__goal.peek()}, coords={self._location}"