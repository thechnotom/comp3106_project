# Represents a path
# Pathfinding elements of this class are heavily inspired by assignment 1

from utilities import print_d, element_at_location, get_location_dictionary, get_movement_modifiers
from Obstacle import Obstacle
from Location import Location
import math
import heapq

class Path:

    # adapted from A1
    class Node:

        def __init__ (self, loc, parent, goal, loc_cost=1):
            self.loc = loc
            self.loc_cost = loc_cost
            self.parent = parent
            self.path_cost = 0
            self.heuristic = Path.calc_heuristic(loc, goal)
            self.priority = 0

        def set_path_cost (self, path_cost):
            self.path_cost = path_cost
            self.priority = self.path_cost + self.heuristic

        def __hash__ (self):
            return hash(loc)

        def __eq__ (self, other):
            return self.loc == other.loc

        def __lt__ (self, other):
            return self.priority < other.priority

        def __str__ (self):
            return f"coords={self.loc}, priority={self.priority}"

    def __init__ (self, start, goal, elements, max_distance=10):
        self.__start = start
        self.__goal = goal
        self.__obstables_dict = self.get_obstacle_dict(elements)
        self.__max_distance = max_distance  # maximum distance from the starting location (using the euclidian distance)
        self.__path = self.get_results()
        self.__pos = 0  # position in the path

    def get_goal (self): return self.__goal

    def is_finished (self): return self.__pos == len(self.__path) - 1

    def get_obstacle_dict (self, elements):
        return get_location_dictionary([x for x in elements if isinstance(x, Obstacle)])

    def get_neighbour_nodes (self, node):
        nodes = []
        for modifier in get_movement_modifiers():
            coords = []
            org_coords = node.loc.get_coords()
            if (len(org_coords) != len(modifier)):
                print_d("Cannot get neighbours (modifier dimension does not match node dimension)")
            for dimension in range(0, len(org_coords)):
                coords.append(org_coords[dimension] + modifier[dimension])
            temp_loc = Location(list(coords))
            # ensure maximum distance from start is not exceeded
            if (self.__start.eucl_dist(temp_loc) > self.__max_distance):
                continue
            # add the element only if it is passable or if it is not an obstacle
            if (temp_loc in self.__obstables_dict):
                temp_element = self.__obstables_dict[temp_loc]
                if (temp_element.is_passable()):
                    nodes.append(Path.Node(temp_loc, node, self.__goal, temp_element.get_cost()))
            else:
                nodes.append(Path.Node(temp_loc, node, self.__goal))
        return nodes

    @staticmethod
    def calc_heuristic (loc, goal):
        return loc.manh_dist(goal)

    # adapted from A1
    def generate_path (self):
        frontier = []
        heapq.heapify(frontier)
        heapq.heappush(frontier, Path.Node(self.__start, None, self.__goal))
        explored_list = []
        while (True):
            if (len(frontier) == 0):
                return None
            leaf = heapq.heappop(frontier)
            explored_list.append(leaf)
            if (leaf.loc == self.__goal):
                return leaf, explored_list
            for node in self.get_neighbour_nodes(leaf):
                curr_path_cost = leaf.path_cost + node.loc_cost  # every move costs the element's cost
                if (node not in frontier and node not in explored_list or node in frontier and curr_path_cost < node.path_cost):
                    node.set_path_cost(curr_path_cost)  # set path cost and recalculate the priority value
                    heapq.heappush(frontier, node)

    # adapted from A1
    def get_results (self):
        curr_node, explored_list = self.generate_path()  # curr_node starts as the final node in the path
        print_d(f"final node: {curr_node}", "path")
        #print_d("explored nodes\n" + self.grid_string(explored_list, -15, -15, 30, 30), "path")
        #print_d("explored nodes\n" + self.grid_string(explored_list, -20, -20, 50, 50), "path")
        if (curr_node is None):
            return None
        path = []

        # move back through the parent nodes until we reach the start
        while (curr_node is not None):
            path.insert(0, curr_node.loc)
            curr_node = curr_node.parent

        return path

    def get_curr_pos (self):
        return self.__path[math.floor(self.__pos)]

    def __advance (self, amount):
        self.__pos = min(self.__pos + amount, len(self.__path) - 1)

    def advance (self, amount):
        pos = self.get_curr_pos()
        self.__advance(amount)
        if (self.__pos < len(self.__path)):
            return pos
        return None

    def grid_string (self, nodes, start_x, start_y, rows, cols):
        result = ""
        locs = [x.loc for x in nodes]
        for x in range(start_x, start_x + cols):
            for y in range(start_y, start_y + rows):
                curr_loc = Location([x, y])
                if (curr_loc == self.__start):
                    result += "s"
                elif (curr_loc == self.__goal):
                    result += "g"
                elif (curr_loc in locs):
                    result += "X"
                else:
                    result += "-"
                result += " "
            result += "\n"
        return result

if __name__ == "__main__":
    path = Path(Location([10, 10]), Location([20, 20]), {}, 20)