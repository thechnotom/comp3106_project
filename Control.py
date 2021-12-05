# Main control class

from utilities import print_d
from Board import Board
from Generator import Generator
from Species import Species
from Location import Location
import time

class Control:

    def __init__ (self):
        print_d("Control does not need to be instantiated")

    @staticmethod
    def start (max_steps=100):
        board = Board.from_csv("initial_conditions/start_1.csv")

        for i in range(0, max_steps):
            if (board.get_step() % 10 == 0):
                print(f"Step: {board.get_step()}")
            board.advance()
            #print(board.get_board_string([0, 0], [30, 30]))
            #print(board.creature_status_string())
            #input("Press ENTER")
            #time.sleep(0.2)

        print(board.population_record_string())

    """
    @staticmethod
    def start ():
        board = Board(top_left=Location([-15, -15]), bottom_right=Location([15, 15]))
        species_1 = Species("tester", health=100, speed=1, vulnerability=2, sight=10)
        species_2 = Species("cool", health=150, speed=2, vulnerability=4, sight=15)

        board.create_creature([1, 2], species_1)
        board.create_creature([5, 3], species_1)
        board.create_creature([-1, -2], species_2)

        board.create_food([3, 4], 10)
        board.create_food([7, 5], 15)
        board.create_food([-7, -7], 12)
        board.create_food([3, 7], 15)
        board.create_food([-2, 9], 11)
        board.create_food([9, 9], 9)
        board.create_food([-2, -9], 11)
        board.create_food([9, -9], 9)

        board.create_shelter([0, 0], 2)
        #board.create_shelter([-8, -8], 2)

        #print(board.get_board_string([0, 0], [10, 10]))
        for i in range(0, 1000):
            print(f"Step: {board.get_step()}")
            board.advance()
            print(board.get_board_string([-15, -15], [30, 30]))
            print(board.creature_status_string())
            #input("Press ENTER")
            time.sleep(0.5)

        print(board.population_record_string())
    """

Control.start(1000)