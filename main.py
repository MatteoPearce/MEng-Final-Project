from ModifyVampireInputFile import modifyVampireInputFile as mvif
from SelectMaterialFile import SelectMaterialFile as smf
from SaveData import saveData
from Regression_Training import TrainGS
from random import randint

class Material_Evolution():

    sweep_grid_size = False,
    sweep_cell_size = False,
    sweep_temperature = False,
    tried_combos = list(),
    max_attempts = 10e4,
    simulation_end = False,
    base_workdir_path = "/home/matteo/Desktop/VAMPIRE_WORKDIR"
    base_materials_path = "/home/matteo/Desktop/VAMPIRE_WORKDIR/Materials"
    input_file_parameters = { "material:file" : ["/Co.mat","/Fe.mat","/Ag.mat"],
                              "dimensions:system-size-x" : [49,99,149,199],
                              "dimensions:system-size-y" : [49,99,149,199],
                              "dimensions:system-size-z" : [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0],
                              "cells:macro-cell-size" : [5,10,15,20],
                              "sim:applied-field-strength" : [0,1e-12,1e-6],
                              "sim:applied-field-unit-vector": [(0,0,1),(0,1,0),(1,0,0)],
                              "sim:temperature" : [0,10,50,100,200,309.65]} #MAKE SURE DEFAULT IS ALWAYS INDEX 0
    new_input_file_parameters = {}

    def __init__(self):
        pass

#----------------------------------------------------------------------------------------------------------------------#

    def select_parameters(self):

        searching_combo = True
        attempts = 0

        while searching_combo:

            self.new_input_file_parameters = {}
            for key,value in self.input_file_parameters.items():
                if (key == "dimensions:system-size-x" or key == "dimensions:system-size-y") and not self.sweep_grid_size:
                    number = 0
                elif (key == "cells:macro-cell-size") and not self.sweep_cell_size:
                    number = 0
                elif (key == "sim:temperature") and not self.sweep_temperature:
                    number = 0
                else:
                    number = randint(0,len(value))

                self.new_input_file_parameters[key] = value[number]

            for combo in self.tried_combos:
                if combo == self.new_input_file_parameters:
                    unique = False
                    break
                else:
                    unique = True

            if unique:
                self.tried_combos.append(self.new_input_file_parameters)
                searching_combo = False

            attempts += 1
            if attempts >= self.max_attempts:
                searching_combo = False
                self.simulation_end = True

#----------------------------------------------------------------------------------------------------------------------#

    def update_input_files(self):

        mvif(self.new_input_file_parameters, self.base_workdir_path)
        smf(self.new_input_file_parameters["material:file"],self.base_materials_path, self.base_workdir_path)


def main() -> None:

    start = Material_Evolution()

if __name__ == "__main__": main()