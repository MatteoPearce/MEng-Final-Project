#!/usr/bin/env python3
from ModifyVampireInputFile import modify_vampire_input as mvif
from SelectMaterialFile import select_material as smf
from SaveData import save_data
from RegressionTraining import train_ridge
from CallVAMPIRE import call_vampire
from random import randint
import numpy as np
from time import time
from ScaleGrid import scale_grid
from GenerateTimeseries import generate_timeseries as GT
from SourcefieldFilemaker import write_sourcefield
from makeHeaders import make_headers
from UdateMagneticDamping import update_damping
from ScaleHeight import scale_height
from ComputeIterations import compute_iterations as CI
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
    
In order to run multiple random searches programmatically, the constructor will have to be modified slightly to accept 
these dictionaries at instantiation.

The string fields:

    base_workdir_path
    base_materials_path
    base_testdata_path
    
are integral to proper execution as they point to the working directory, materials library and data retention folders. 

The order of processes is:

0. generate NARMA10
0. work out how many iterations 
1. select parameters  <-----------,
2. update input files             |
3. run simulation                 |
4. train model and compute NRMSE   |
5. save data _____________________/
"""

class MaterialEvolution():

    tried_combos: list = list() # populates with sim params of each loop. Is compared to check for uniqueness of combos
    max_attempts: float = 10e4 # how many attempts
    current_best_setup: dict = dict() # best param combination of unseen data
    main_timer : float = None # tracks duration of entire random search
    iteration_counter: int = 0 # tracks progress
    iteration_times : list = list() # tracks duration of each iteration
    narma_input: np.ndarray = None # NARMA10
    narma_output: np.ndarray = None  # NARMA10
    simulation_end: bool = False
    random_scaling: bool = False
    random_input_locs: bool = False
    signal_strength: float = 1.0
    best_result = np.inf # current best, starts at "infinity", 0 being desirable
    base_workdir_path: str = "/home/matteo/Desktop/VAMPIRE_WORKDIR" # working directory with materials folder and vampire binary "/home/matteo/Desktop/VAMPIRE_WORKDIR"
    base_materials_path: str = "/home/matteo/Desktop/VAMPIRE_WORKDIR/Materials" # materials folder in working directory "/home/matteo/Desktop/VAMPIRE_WORKDIR/Materials"
    base_testdata_path: str = "/home/matteo/Desktop/VAMPIRE_TEST_RESULTS" # results depot "/home/matteo/Desktop/VAMPIRE_TEST_RESULTS"
    input_file_parameters: dict = { "material:file" : ["Fe.mat"], #"Co.mat"],#,"Fe.mat","Ni.mat"],
                                    "dimensions:system-size-x" : [49],
                                    "dimensions:system-size-y" : [49],
                                    "dimensions:system-size-z" : [2.866,5.732],
                                    "cells:macro-cell-size" : [2,2.5],
                                    "sim:applied-field-strength" : [0],
                                    "sim:applied-field-unit-vector": [(0,0,1)],
                                    "sim:temperature" : [0]} # input file parameters and the values to explore.
    input_file_units: dict = { "material:file" : "",
                              "dimensions:system-size-x" : " !nm",
                              "dimensions:system-size-y" : " !nm",
                              "dimensions:system-size-z" : " !A",
                              "cells:macro-cell-size" : " !nm",
                              "sim:applied-field-strength" : " !T",
                              "sim:applied-field-unit-vector": "",
                              "sim:temperature" : ""} # default units for input file parameters. must mirror input_file_parameters keys
    other_sweep_parameters: dict = { "intrinsic magnetic damping" : np.arange(0.001,0.501,0.05),#[0.001,0.005,0.01,0.05,0.1,0.2,0.3,0.4,0.5],
                                   "field intensity input scaling": np.arange(0.1,2,0.1)}#[-3,-2.5,-2,-1.5,-1,-0.5,0.5,1,1.5,2,2.5,3]} # non-input-file parameters to explore
    all_sweep_parameters: dict = dict() # collation of input_file_parameters and other_sweep_parameters
    new_input_file_parameters: dict = dict() # current combination of input file exploration parameters. new with every iteration
    new_other_sweep_parameters: dict = dict() # current combination of non-input-file exploration parameters. new with every iteration

#----------------------------------------------------------------------------------------------------------------------#

    def __init__(self , input_length,signal_strength,random_scaling,random_input_locs):

        if signal_strength is not None:
            self.signal_strength = signal_strength
        if random_scaling is not None:
            self.random_scaling = random_scaling
        if random_input_locs is not None:
            self.random_input_locs = random_input_locs
        self.main_timer = time() # search start time
        self.input_length = input_length # total simulation timesteps
        self.narma_input , self.narma_output = GT(stop_time=input_length)# generate NARMA10
        self.narma_input = self.narma_input * self.signal_strength
        self.narma_output = self.narma_output * self.signal_strength
        self.iterations_total = CI(self.base_materials_path,self.input_file_parameters.copy(),self.other_sweep_parameters.copy()) # compute number of iterations
        self.main_loop() # start search

#----------------------------------------------------------------------------------------------------------------------#

    def main_loop(self):

            while not self.simulation_end: # end when no unique combinations found
                print(f"\n WORKING ON ITERATION {self.iteration_counter} / {self.iterations_total} \n")
                start_time = time() # time per iteration
                self.select_parameters()
                if self.simulation_end:
                    pass
                else:
                    self.update_input_files()
                    self.run_simulation()
                    self.reservoir_computing() # fitting, NRMSE, save data
                    self.iteration_counter += 1
                end_time = time() # time per iteration
                self.iteration_times.append(end_time - start_time) # time of every iteration

            # communicate end, best run, save timing data
            print("SIMULATION ENDED, BEST SETUP AND RESULT:\n")
            print(self.current_best_setup)

            end_time = time() # search end
            self.main_timer = end_time - self.main_timer # total search time
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
        attempts = 0 # counter for simulation end condition

        while searching_combo:

            self.new_input_file_parameters = dict()
            # from each input param select one value at random
            for key,value in self.input_file_parameters.items():
                number = randint(0,len(value)-1)
                self.new_input_file_parameters[key] = value[number]

            # from each other param select one value at random
            for key, value in self.other_sweep_parameters.items():
                number = randint(0, len(value) - 1)
                self.new_other_sweep_parameters[key] = value[number]

            # convert height to nearest multiple of unit cell size
            new_height = scale_height(self.base_materials_path,self.new_input_file_parameters["material:file"], self.new_input_file_parameters["dimensions:system-size-z"])
            self.new_input_file_parameters["dimensions:system-size-z"] = new_height

            # pick random compatible film and grid size
            new_x, new_y, new_grid = scale_grid(x_dims=self.input_file_parameters["dimensions:system-size-x"],
                                               y_dims=self.input_file_parameters["dimensions:system-size-y"],
                                               cell_dim=self.input_file_parameters["cells:macro-cell-size"])

            self.new_input_file_parameters["dimensions:system-size-x"] = new_x
            self.new_input_file_parameters["dimensions:system-size-y"] = new_y
            self.new_input_file_parameters["cells:macro-cell-size"] = new_grid

            # collate input and other parameters
            self.all_sweep_parameters.update(self.new_input_file_parameters)
            self.all_sweep_parameters.update(self.new_other_sweep_parameters)

            # combo is assumed unique until disproven
            if len(self.tried_combos) == 0:
                unique = True
            else:
                unique = True
                # check all tried combos, if match found, not unique
                for combo in self.tried_combos:
                    if combo == self.all_sweep_parameters:
                        unique = False
                        break

            if unique: # combo found
                self.tried_combos.append(self.all_sweep_parameters.copy()) # record combo
                searching_combo = False # exit loop and run sim


            if attempts >= self.max_attempts: # max attempts = 10e4
                searching_combo = False # exit loop
                self.simulation_end = True # end search

            attempts += 1

#----------------------------------------------------------------------------------------------------------------------#

    def update_input_files(self):

        # calc how many cells for each dim, for constructing sourcefield.txt headers
        cells_perX = int((self.new_input_file_parameters["dimensions:system-size-x"] + 1)  / self.new_input_file_parameters["cells:macro-cell-size"])
        cells_perY = int((self.new_input_file_parameters["dimensions:system-size-y"] + 1)  / self.new_input_file_parameters["cells:macro-cell-size"])

        headers = make_headers(cells_perX, cells_perY)

        # convert all exploration params to string and add units
        for key1, key2 in zip(self.new_input_file_parameters.keys(), self.input_file_units.keys()):
            self.new_input_file_parameters[key1] = str(self.new_input_file_parameters[key1]) + self.input_file_units[key2]

        # original timeseries never changes during a search, but gets scaled and rewritten if input scaling explored
        if self.random_scaling:
            scaled_input = self.narma_input.copy() * np.random.rand(self.input_length,) * self.new_other_sweep_parameters["field intensity input scaling"]
        else:
            scaled_input = self.narma_input.copy() * self.new_other_sweep_parameters["field intensity input scaling"]

        # rewrite sourcefield.txt
        write_sourcefield(output_path=self.base_workdir_path,
                          rows=scaled_input.shape[0],
                          timeseries=scaled_input,
                          columns=int(cells_perX * cells_perY),
                          all_same=True,
                          headers=headers,
                          random_input_locs=self.random_input_locs)

        # copy material file to workdir, modify input file, change magnetic damping in .mat file
        smf(self.new_input_file_parameters["material:file"], self.base_materials_path, self.base_workdir_path) #IMPORTANT THAT THIS GOES FIRST
        mvif(self.new_input_file_parameters.copy(), self.base_workdir_path)
        update_damping(self.base_workdir_path,self.new_other_sweep_parameters["intrinsic magnetic damping"])

        # remove reservoir_output.txt. ensures that if there is a failure, the previous iteration output isn't used
        for file in os.listdir(self.base_workdir_path):
            filename = os.fsdecode(file)
            if filename == "reservoir_output.txt":
                os.remove(os.path.join(self.base_workdir_path, file))

#----------------------------------------------------------------------------------------------------------------------#

    def run_simulation(self):

        call_vampire(self.base_workdir_path,parallel=False,debug_mode=False)

#----------------------------------------------------------------------------------------------------------------------#

    def reservoir_computing(self):

        # NRMSE on unseen data, NRMSE on seen data, unseen trace, prediction
        best_result, training_result, y, y_pred = train_ridge(self.base_workdir_path,self.narma_output)

        # None is returned if failed to fit model. occurs if sim outputs NaNs
        if best_result is not None:
            data_to_save = {"y": y,
                            "y_pred":y_pred,
                            "training_NRMSE":training_result,
                            "NRMSE": best_result,
                            "signal_strength": self.signal_strength}

            # exploration params and results
            data_to_save.update(self.all_sweep_parameters.copy())

            # update best combo, considering only NRMSE of prediction of unseen data
            if best_result < self.best_result:
                self.best_result = best_result
                self.current_best_setup = self.all_sweep_parameters.copy()
                self.current_best_iteration = self.iteration_counter

            # saves input files, plot of prediction, accuracy scores
            save_data(data=data_to_save,
                     dir_name="/" + str(self.iteration_counter),
                     save_path=self.base_testdata_path,
                     workdir_path=self.base_workdir_path)

        else:
            # input files and exploration params of failures are saved so failure can be replicated
            print("FAILED ON:")
            print(self.all_sweep_parameters)
            data_to_save = self.all_sweep_parameters
            save_data(data=data_to_save,
                     dir_name="/" + str(self.iteration_counter) + " FAILED",
                     save_path=self.base_testdata_path,
                     workdir_path=self.base_workdir_path,
                     Failed=True)

#----------------------------------------------------------------------------------------------------------------------#

def main() -> None:
    signal_strenth = 1
    random_scaling = True
    random_input_locs = True
    input_length = 1000
    start = MaterialEvolution(input_length=input_length,
                              signal_strength=signal_strenth,
                              random_scaling=random_scaling,
                              random_input_locs=random_input_locs)

if __name__ == "__main__": main()