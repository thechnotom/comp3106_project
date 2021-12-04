# Main control class

from utilities import print_d
from Board import Board
from Generator import Generator
from Species import Species

class Control:

    def __init__ (self):
        print_d("Control does not need to be instantiated")

    @staticmethod
    def start ():
        board = Board()
        species = Species("tester", health=100, speed=1, vulnerability=2, sight=10)

        board.create_creature([1, 2], species)
        board.create_food([3, 4], 10)
        #board.create_food([7, 5], 5)
        board.create_food([-7, -7], 7)
        board.create_shelter([0, 0], 2)

        print(board.get_board_string([0, 0], [10, 10]))
        for i in range(0, 1000):
            print(f"Step: {board.get_step()}")
            board.advance()
            print(board.get_board_string([-15, -15], [30, 30]))
            print(board.creature_health_string())
            input("Press ENTER")

Control.start()