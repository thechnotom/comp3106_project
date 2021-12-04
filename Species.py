# Representation of a creature's species/attributes

class Species:

    def __init__ (self, name, health=100, speed=1, vulnerability=1, sight=10):
        self.__name = name
        self.__health = health
        self.__speed = speed
        self.__vulnerability = vulnerability  # amount of health lost per iteration
        self.__sight = sight

    def get_name (self): return self.__name

    def get_attributes (self):
        return {
            "health" : self.__health,
            "speed" : self.__speed,
            "vulnerability" : self.__vulnerability,
            "sight" : self.__sight
        }

    def __hash__ (self):
        return hash(self.__name)

    def __eq__ (self, other):
        return self.__name == other.get_name()

    def __str__ (self):
        return f"Species: n={self.__name}, h={self.__health}, sp={self.__speed}, v={self.__vulnerability}, si={self.__sight}"