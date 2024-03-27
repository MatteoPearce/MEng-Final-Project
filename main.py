from ModifyVampireInputFile import modifyVampireInputFile as mvif
from SelectMaterialFile import SelectMaterialFile as smf
from SaveData import saveData
from Regression_Training import TrainGS
from CallVAMPIRE import CallVAMPIRE
from random import randint

class Material_Evolution():

    sweep_grid_size = False,
    sweep_cell_size = False,
    sweep_temperature = False,
    tried_combos = list(),
    max_attempts = 10e4,
    iteration_counter = 0
    simulation_end = False,
    current_best_result = 1,
    current_best_iteration = None,
    current_best_setup = dict(),
    base_workdir_path = "/home/matteo/Desktop/VAMPIRE_WORKDIR"
    base_materials_path = "/home/matteo/Desktop/VAMPIRE_WORKDIR/Materials"
    base_testdata_path = "/home/matteo/Desktop/VAMPIRE_TEST_RESULTS"
    input_file_parameters = { "material:file" : ["/Co.mat","/Fe.mat","/Ag.mat"],
                              "dimensions:system-size-x" : [49,99,149,199],
                              "dimensions:system-size-y" : [49,99,149,199],
                              "dimensions:system-size-z" : [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0],
                              "cells:macro-cell-size" : [5,10,15,20],
                              "sim:applied-field-strength" : [0,1e-12,1e-6],
                              "sim:applied-field-unit-vector": [(0,0,1),(0,1,0),(1,0,0)],
                              "sim:temperature" : [0,10,50,100,200,309.65]} #MAKE SURE DEFAULT IS ALWAYS INDEX 0
    new_input_file_parameters = dict()

#----------------------------------------------------------------------------------------------------------------------#

    def __init__(self):
        self.main_loop()

#----------------------------------------------------------------------------------------------------------------------#

    def main_loop(self):

        while not self.simulation_end:

            self.select_parameters()
            self.update_input_files()
            self.run_simulation()
            self.reservoir_computing()
            self.iteration_counter += 1

        print("SIMULATION ENDED, BEST SETUP AND RESULT:\n")
        print(self.current_best_setup)
        print(f"best result: NRMSE = {0:.2f}".format(self.current_best_result))

        with open(self.base_workdir_path + "/best_iteration.txt", "w") as file:
            file.writelines(f"best interation number: {self.current_best_iteration}")
            file.close()

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

            if len(self.tried_combos) == 0:
                unique = True
            else:

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

#----------------------------------------------------------------------------------------------------------------------#

    def run_simulation(self):

        CallVAMPIRE(self.base_workdir_path,parallel=False,debug_mode=False)
        print("simulation done")

#----------------------------------------------------------------------------------------------------------------------#

    def reservoir_computing(self):

        best_result, y, y_pred = TrainGS(self.base_workdir_path)

        data_to_save = {"y": y,
                        "y_pred":y_pred,
                        "NRMSE": best_result}

        data_to_save.update(self.new_input_file_parameters)

        if best_result < self.current_best_result:
            self.current_best_result = best_result
            self.current_best_setup = self.new_input_file_parameters
            self.current_best_iteration = self.iteration_counter
            print(f"\nnew best found! current NRMSE: {0:.2f}".format(best_result))

        saveData(data=data_to_save,
                 dir_name=str(self.iteration_counter),
                 save_path=self.base_testdata_path,
                 workdir_path=self.base_workdir_path)

#----------------------------------------------------------------------------------------------------------------------#

def main() -> None:

    start = Material_Evolution()

if __name__ == "__main__": main()