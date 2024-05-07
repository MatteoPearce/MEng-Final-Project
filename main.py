#!/usr/bin/env python3
from ModifyVampireInputFile import modifyVampireInputFile as mvif
from SelectMaterialFile import SelectMaterialFile as smf
from SaveData import saveData
from Regression_Training import TrainGS
from CallVAMPIRE import CallVAMPIRE
from random import randint
import numpy as np
from time import time
from ScaleGrid import scaleGrid
from GenerateTimeseries import GenerateTimeseries as GT
from Sourcefield_Filemaker import filemaker
from makeHeaders import makeHeaders
from UdateMagneticDamping import updateDamping
from ScaleHeight import scaleHeight
from ComputeIterations import computeIterations as CI
import os

"""
MAIN CLASS FOR RANDOM SEARCH ALGORITHM.

This project uses the university of York's in-house software package Vampire, a state-of-the-art atomistic simulator 
for magnetic nanomaterials developed by Evans et al., (https://vampire.york.ac.uk/). 

An arbitrary NARMA10 timeseries is generated with the timesynth library and saved to a sourcefield.txt file in the 
working directory where the Vampire binary is housed. Subsequently, a random search algorithm generates an untested 
configuration of simulation parameters, modifies an input.txt and material.mat file required by Vampire, invokes 
Vampire, extracts the output from the reservoir_output.txt file and uses supervision learning to train a perceptron 
layer with a ridge regression optimisation function. The objective is to find a combination of material and associated 
physical parameters that can excel as a reservoir at body temperature with input fields of a magnitude as found 
in biomagnetism.

To change the exploration parameters modify the fields:

    input_file_parameters
    other_sweep_parameters
    
In order to run multiple random searches programatically, the constructor will have to be modified slightly to accept 
these dictionaries at instantiation.

The string fields:

    base_workdir_path
    base_materials_path
    base_testdata_path
    
are integral to proper execution as they point to the working directory, materials library and data retention folders. 

"""

class MaterialEvolution():

    tried_combos: list = list() # populates with sim params of each loop. Is compared to check for uniqueness of combos.
    max_attempts: float = 10e4 # how many attempts before deciding all combos exhausted.
    iteration_counter: int = 0 # for printing progress and saving data.
    iterations_total: int = None # for printing progress.
    simulation_end: bool = False # True when all combos tried.
    current_best_result: float = np.inf # best NMSE on unseen data.
    current_best_training: float = np.inf # best NMSE on unseen data.
    current_best_iteration: int = None
    current_best_setup: dict = dict() # best param combination of unseen data.
    main_timer : float = None
    iteration_times : list = list()
    timeseries: np.ndarray = None
    base_workdir_path: str = "/home/matteo/Desktop/VAMPIRE_WORKDIR"
    base_materials_path: str = "/home/matteo/Desktop/VAMPIRE_WORKDIR/Materials"
    base_testdata_path: str = "/home/matteo/Desktop/VAMPIRE_TEST_RESULTS"
    input_file_parameters: dict = { "material:file" : ["Co.mat","Fe.mat","Ni.mat"],#
                              "dimensions:system-size-x" : [49],#149,199],
                              "dimensions:system-size-y" : [49],#,99,149,199],
                              "dimensions:system-size-z" : [0.1],#np.arange(0.1,1,0.1),
                              "cells:macro-cell-size" : [5,10],#15,20],
                              "sim:applied-field-strength" : [0],#,1e-24,1e-12,1e-6],
                              "sim:applied-field-unit-vector": [(0,0,1)],#,(0,1,0),(1,0,0)],
                              "sim:temperature" : [309.65]} #MAKE SURE DEFAULT IS ALWAYS INDEX 0
    input_file_units: dict = { "material:file" : "",
                              "dimensions:system-size-x" : " !nm",
                              "dimensions:system-size-y" : " !nm",
                              "dimensions:system-size-z" : " !A",
                              "cells:macro-cell-size" : " !nm",
                              "sim:applied-field-strength" : " !T",
                              "sim:applied-field-unit-vector": "",
                              "sim:temperature" : ""}
    other_sweep_parameters: dict = { "intrinsic magnetic damping" : [0.001,0.01,0.1,0.5,1],
                                   "field intensity input scaling": [-3e-13,-2e-13,-1e-13,1e-13,2e-13,3e-13]}
    all_sweep_parameters: dict = dict()
    new_input_file_parameters: dict = dict()
    new_other_sweep_parameters: dict = dict()

#----------------------------------------------------------------------------------------------------------------------#

    def __init__(self , input_length):

        self.main_timer = time()
        self.input_length = input_length
        self.timeseries = GT(stop_time=input_length)
        self.iterations_total = CI(self.base_workdir_path,self.input_file_parameters,self.other_sweep_parameters)
        self.main_loop()

#----------------------------------------------------------------------------------------------------------------------#

    def main_loop(self):

            while not self.simulation_end:
                print(f"\n WORKING ON ITERATION {self.iteration_counter+1} / {self.iterations_total} \n")
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

            with open(self.base_testdata_path + "/sim_data.txt", "w") as file:
                file.writelines(f"best iteration number: {self.current_best_iteration}\n")
                file.writelines(f"total time : {round((self.main_timer / 60) / 60, 2)} hours\n")
                file.writelines(f"average iteration time : {round(average_time, 2)} seconds \n\n")

#----------------------------------------------------------------------------------------------------------------------#

    def select_parameters(self):

        searching_combo = True
        attempts = 0

        while searching_combo:

            self.new_input_file_parameters = {}
            for key,value in self.input_file_parameters.items():
                number = randint(0,len(value)-1)
                self.new_input_file_parameters[key] = value[number]

            new_height = scaleHeight(self.base_materials_path,self.new_input_file_parameters["material:file"], self.new_input_file_parameters["dimensions:system-size-z"])
            self.new_input_file_parameters["dimensions:system-size-z"] = new_height

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
    start = MaterialEvolution(input_length)

if __name__ == "__main__": main()