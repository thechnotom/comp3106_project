# Main control class

from utilities import print_d, import_json
from Board import Board
from Generator import Generator
from Species import Species
from Location import Location
import time
from Graph import Graph
import sys

class Control:

    def __init__ (self):
        print_d("Control does not need to be instantiated")

    @staticmethod
    def start ():
        config_filename = "config.json"
        if (len(sys.argv) == 2):
            config_filename = sys.argv[1]
        config = import_json(config_filename)
        board = Board.from_csv(config["files"]["layout"], config_filename)
        options = config["control"]
        max_steps = options["max_steps"]

        start_time = time.time()
        try:
            for i in range(0, max_steps):
                if (options["show_every_X_steps"] > 0 and board.get_step() % options["show_every_X_steps"] == 0):
                    print(f"Step: {board.get_step()}/{max_steps}")
                board.advance()
                if (options["show_every_X_boards"] > 0 and board.get_step() % options["show_every_X_boards"] == 0):
                    print(board.get_board_string(board.get_origin_coords(), board.get_board_dimensions()))
                    print(board.creature_status_string())
                    if (options["wait_for_user"]):
                        input("Press ENTER")
                    if (options["delay"] > 0):
                        time.sleep(options["delay"])
        except KeyboardInterrupt:
            print("Caught Ctrl+C")
        end_time = time.time()
        print(f"Simulation time: {round(end_time - start_time, 2)} seconds")
        print(f"Completed {board.get_step()}/{max_steps} steps")

        if (options["show_graphs"]):
            print("Creating graphs")
            last_step = board.get_step()
            population_record = board.get_population_record()
            food_record = board.get_food_record()
            graph = Graph()
            graph.create_species_graph(Graph.convert_population_record(population_record, last_step))
            graph.create_food_graph(Graph.convert_food_record(food_record, last_step))
            try:
                Graph.show_graphs()
            except KeyboardInterrupt:
                print("Caught Ctrl+C")

    @staticmethod
    def print_information ():
        print("=========================")
        print("Thomas Roller (101072857)")
        print("COMP 3106 A (Fall 2021)")
        print("Final Project")
        print("=========================")