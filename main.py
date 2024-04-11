from ModifyVampireInputFile import modifyVampireInputFile as mvif
from SelectMaterialFile import SelectMaterialFile as smf
from SaveData import saveData
from Regression_Training import TrainGS
from CallVAMPIRE import CallVAMPIRE
from random import randint
import numpy as np
from time import time
from ScaleGrid import scaleGrid
from GenerateTimeseries import GenerateTimeseries as GT #https://analyticsindiamag.com/guide-to-timesynth-a-python-library-for-synthetic-time-series-generation/#h-narma-series
from Sourcefield_Filemaker import filemaker
from makeHeaders import makeHeaders
from UdateMagneticDamping import updateDamping
import os

class Material_Evolution():

    sweep_grid_size: bool = True
    sweep_temperature: bool = False
    tried_combos: list = list()
    max_attempts: float = 10e4
    iteration_counter: int = 0
    simulation_end: bool = False
    current_best_result: float = np.inf
    current_best_training: float = np.inf
    current_best_iteration: int = None
    current_best_setup: dict = dict()
    best_per_materials : list[dict()] = list(dict())
    main_timer : float = None
    iteration_times : list = list()
    timeseries: np.ndarray = None
    base_workdir_path: str = "/home/matteo/Desktop/VAMPIRE_WORKDIR"
    base_materials_path: str = "/home/matteo/Desktop/VAMPIRE_WORKDIR/Materials"
    base_testdata_path: str = "/home/matteo/Desktop/VAMPIRE_TEST_RESULTS"
    input_file_parameters: dict = { "material:file" : ["Co.mat","Fe.mat","Ni.mat",],#"Ag.mat"],
                              "dimensions:system-size-x" : [49,99,149,199],
                              "dimensions:system-size-y" : [49,99,149,199],
                              "dimensions:system-size-z" : [0.1],#np.arange(0.1,1,0.1),
                              "cells:macro-cell-size" : [5,10,15,20],
                              "sim:applied-field-strength" : [0],#,"1e-24 !T","1e-12 !T","1e-6 !T"],
                              "sim:applied-field-unit-vector": [(0,0,1)],#,(0,1,0),(1,0,0)],
                              "sim:temperature" : [0]} #MAKE SURE DEFAULT IS ALWAYS INDEX 0
    input_file_units: dict = { "material:file" : "",
                              "dimensions:system-size-x" : " !nm",
                              "dimensions:system-size-y" : " !nm",
                              "dimensions:system-size-z" : " !A",
                              "cells:macro-cell-size" : " !nm",
                              "sim:applied-field-strength" : " !T",
                              "sim:applied-field-unit-vector": "",
                              "sim:temperature" : ""}
    other_sweep_parameters: dict = { "intrinsic magnetic damping" : [0.3,0.4,0.5],#0.001,0.1,0.5,1],
                                   "field intensity input scaling": [-2,-1.5,-1,-0.5]}
    all_sweep_parameters: dict = dict()
    new_input_file_parameters: dict = dict()
    new_other_sweep_parameters: dict = dict()

#----------------------------------------------------------------------------------------------------------------------#

    def __init__(self , input_length):

        self.main_timer = time()
        self.input_length = input_length
        self.timeseries = GT(stop_time=input_length)
        self.main_loop()

#----------------------------------------------------------------------------------------------------------------------#

    def main_loop(self):

            while not self.simulation_end:
                start_time = time()
                self.select_parameters()
                if self.simulation_end:
                    pass
                else:
                    self.update_input_files()
                    self.run_simulation()
                    self.reservoir_computing()
                    self.iteration_counter += 1
                end_time = time()
                self.iteration_times.append(end_time - start_time)

            print("SIMULATION ENDED, BEST SETUP AND RESULT:\n")
            print(self.current_best_setup)
            print(f"best result: NRMSE = {self.current_best_result}")

            end_time = time()
            self.main_timer = end_time - self.main_timer
            average_time = sum(self.iteration_times) / len(self.iteration_times)
            print(f"\nelapsed time: {round((self.main_timer / 60) / 60, 2)} hours")
            print(f"\naverage time per iteration: {round(average_time, 2)} seconds")

            with open(self.base_testdata_path + "/best_iteration.txt", "w") as file:
                file.writelines(f"best iteration number: {self.current_best_iteration}\n")
                file.writelines(f"total time : {round((self.main_timer / 60) / 60, 2)} hours\n")
                file.writelines(f"average iteration time : {round(average_time, 2)} seconds \n\n")
                file.writelines("#------------------------------------------------------------------------------------#\n\n")
                file.writelines("best per material:\n\n")
                for material in self.best_per_materials:
                    for key in material.keys():
                        file.writelines(str(key + " = " + str(material[key]) + "\n"))
                    file.writelines("\n")
                file.close()

#----------------------------------------------------------------------------------------------------------------------#

    def select_parameters(self):

        searching_combo = True
        attempts = 0

        while searching_combo:

            self.new_input_file_parameters = {}
            for key,value in self.input_file_parameters.items():
                if (key == "dimensions:system-size-x" or key == "dimensions:system-size-y"):
                    number = 0
                elif (key == "cells:macro-cell-size"):
                    number = 0
                elif (key == "sim:temperature") and not self.sweep_temperature:
                    number = 0
                else:
                    number = randint(0,len(value)-1)

                self.new_input_file_parameters[key] = value[number]

            if self.sweep_grid_size:

                new_x, new_y, new_grid = scaleGrid(x_dims=self.input_file_parameters["dimensions:system-size-x"],
                                                   y_dims=self.input_file_parameters["dimensions:system-size-y"],
                                                   cell_dim=self.input_file_parameters["cells:macro-cell-size"],
                                                   save_path=self.base_workdir_path,
                                                   timeseries=self.timeseries)

                self.new_input_file_parameters["dimensions:system-size-x"] = new_x
                self.new_input_file_parameters["dimensions:system-size-y"] = new_y
                self.new_input_file_parameters["cells:macro-cell-size"] = new_grid

            for key, value in self.other_sweep_parameters.items():
                number = randint(0, len(value) - 1)
                self.new_other_sweep_parameters[key] = value[number]

            self.all_sweep_parameters.update(self.new_input_file_parameters)
            self.all_sweep_parameters.update(self.new_other_sweep_parameters)

            if len(self.tried_combos) == 0:
                unique = True
            else:
                unique = True
                for combo in self.tried_combos:
                    if combo == self.all_sweep_parameters:
                        unique = False
                        break

            if unique:
                self.tried_combos.append(self.all_sweep_parameters.copy())
                searching_combo = False


            if attempts >= self.max_attempts:
                searching_combo = False
                self.simulation_end = True

            attempts += 1

#----------------------------------------------------------------------------------------------------------------------#

    def update_input_files(self):

        cells_perX = int((self.new_input_file_parameters["dimensions:system-size-x"] + 1)  / self.new_input_file_parameters["cells:macro-cell-size"])
        cells_perY = int((self.new_input_file_parameters["dimensions:system-size-y"] + 1)  / self.new_input_file_parameters["cells:macro-cell-size"])

        headers = makeHeaders(cells_perX, cells_perY)

        for key1, key2 in zip(self.new_input_file_parameters.keys(), self.input_file_units.keys()):
            self.new_input_file_parameters[key1] = str(self.new_input_file_parameters[key1]) + \
                                                   self.input_file_units[key2]

        scaled_timeseries = self.timeseries.copy() * self.new_other_sweep_parameters["field intensity input scaling"]

        filemaker(output_path=self.base_workdir_path,
                  rows=self.timeseries.shape[0],
                  timeseries=scaled_timeseries,
                  columns=int(cells_perX * cells_perY),
                  all_same=True,
                  headers=headers)

        smf(self.new_input_file_parameters["material:file"], self.base_materials_path, self.base_workdir_path) #IMPORTANT THAT THIS GOES FIRST
        mvif(self.new_input_file_parameters.copy(), self.base_workdir_path)
        updateDamping(self.base_workdir_path,self.new_other_sweep_parameters["intrinsic magnetic damping"])

        for file in os.listdir(self.base_workdir_path):
            filename = os.fsdecode(file)
            if filename == "reservoir_output.txt":
                os.remove(os.path.join(self.base_workdir_path, file))

#----------------------------------------------------------------------------------------------------------------------#

    def run_simulation(self):

        CallVAMPIRE(self.base_workdir_path,parallel=False,debug_mode=False)

#----------------------------------------------------------------------------------------------------------------------#

    def reservoir_computing(self):

        best_result, best_training, y, y_pred = TrainGS(self.base_workdir_path)

        if best_result is not None:
            data_to_save = {"y": y,
                            "y_pred":y_pred,
                            "training_NRMSE":best_training,
                            "NRMSE": best_result}

            params = self.all_sweep_parameters.copy()
            params["iteration"] = self.iteration_counter
            params["training_NRMSE"] = best_training
            params["NRMSE"] = best_result

            data_to_save.update(self.all_sweep_parameters.copy())

            if best_result < self.current_best_result:
                self.current_best_result = best_result
                self.current_best_training = best_training
                self.current_best_setup = self.all_sweep_parameters.copy()
                self.current_best_iteration = self.iteration_counter

            if len(self.best_per_materials) == 0:
                self.best_per_materials.append(params)
            else:
                best_material_changed = False
                for index,mat in enumerate(self.best_per_materials):
                    if mat["material:file"] == self.all_sweep_parameters["material:file"]:
                        if best_result < mat["NRMSE"]:
                            self.best_per_materials[index] = params
                            best_material_changed = True
                            break

                if not best_material_changed:
                    self.best_per_materials.append(params)

            saveData(data=data_to_save,
                     dir_name="/" + str(self.iteration_counter),
                     save_path=self.base_testdata_path,
                     workdir_path=self.base_workdir_path)

        else:

            print("FAILED ON:")
            print(self.all_sweep_parameters)
            data_to_save = self.all_sweep_parameters
            saveData(data=data_to_save,
                     dir_name="/" + str(self.iteration_counter) + " FAILED",
                     save_path=self.base_testdata_path,
                     workdir_path=self.base_workdir_path,
                     Failed=True)

#----------------------------------------------------------------------------------------------------------------------#

def main() -> None:

    input_length = 500
    start = Material_Evolution(input_length)

if __name__ == "__main__": main()