# Convert statistic data and create graphs

import matplotlib.pyplot as plt

class Graph:

    def __init__ (self):
        self.__count = 0

    @staticmethod
    def convert_population_record (population_record, num_steps):
        result = {}
        species_last_record = {}  # last recorded population for all species
        # walk through all recorded time steps
        for step in range(0, num_steps):
            if (step in population_record):
                for species in population_record[step]:
                    species_last_record[species] = population_record[step][species]
            for species in species_last_record:
                if (species not in result):
                    result[species] = {"step" : [], "population" : []}
                result[species]["step"].append(step)
                result[species]["population"].append(species_last_record[species])
        return result

    @staticmethod
    def convert_population_record_depr (population_record):
        result = {}
        # walk through all recorded time steps
        for record in population_record:
            # walk through all species noted at current time step
            for species in population_record[record]:
                if (species not in result):
                    result[species] = {"step" : [], "population" : []}
                result[species]["step"].append(record)
                result[species]["population"].append(population_record[record][species])
        return result

    def convert_food_record (food_record, num_steps):
        result = {"step" : [], "amount" : []}
        food_last_record = 0
        for step in range(0, num_steps):
            if (step in food_record):
                food_last_record = food_record[step]
            result["step"].append(step)
            result["amount"].append(food_last_record)
        return result

    @staticmethod
    def convert_food_record_depr (food_record):
        result = {"step" : [], "amount" : []}
        for record in food_record:
            result["step"].append(record)
            result["amount"].append(food_record[record])
        return result

    def create_species_graph (self, data, species=None):
        plt.figure(self.__count)
        species_list = data.keys()
        if (species is not None):
            species_list = species
        for species in species_list:
            plt.plot(data[species]["step"], data[species]["population"], label=species)
        plt.xlabel("Step Number")
        plt.ylabel("Population")
        plt.title("Population vs. Time")
        plt.legend()
        self.__count += 1

    def create_food_graph (self, data):
        plt.figure(self.__count)
        plt.plot(data["step"], data["amount"])
        plt.xlabel("Step Number")
        plt.ylabel("Amount")
        plt.title("Food vs. Time")
        self.__count += 1

    @staticmethod
    def show_graphs ():
        plt.show()