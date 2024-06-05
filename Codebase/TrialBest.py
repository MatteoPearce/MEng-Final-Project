#!/usr/bin/env python3
import numpy as np
import os
import matplotlib.pyplot as plt
from GenerateTimeseries import generate_timeseries as GT
from ModifyVampireInputFile import modify_vampire_input as mvif
from SelectMaterialFile import select_material as smf
from makeHeaders import make_headers
from SourcefieldFilemaker import write_sourcefield
from UdateMagneticDamping import update_damping
from ScaleHeight import scale_height
from CallVAMPIRE import call_vampire
from RegressionTraining import train_ridge

"""
TRIAL BEST RUNS X TIMES.

This class has been adapted from main.py and shares most of the functionality. The main difference is that the simulation
parameters are passed to the constructor and there is no random selection. The constructor must receive a best combination
of parameters for each of the three materials. See the example at the bottom of this file.

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
4. train model and compute NRMSE  |
5. save data _____________________/
"""


class TrialBest():

    best_Fe: dict = dict()
    best_Ni: dict = dict()
    best_Co: dict = dict()
    current_data: dict = dict()
    materials: list = list()
    Fe_list: dict = {"NRMSE": list(), "training_NRMSE": list()}
    Ni_list: dict = {"NRMSE": list(), "training_NRMSE": list()}
    Co_list: dict = {"NRMSE": list(), "training_NRMSE": list()}

    trials:int = 10
    trial_length = 500
    signal_strength: float = 1e-13

    random_scaling: bool = False
    random_input_locs: bool = False

    NARMA_input: np.ndarray
    NARMA_output: np.ndarray

    base_workdir_path: str = "/home/matteo/Desktop/VAMPIRE_WORKDIR"  # working directory with materials folder and vampire binary
    base_materials_path: str = "/home/matteo/Desktop/VAMPIRE_WORKDIR/Materials"  # materials folder in working directory
    base_testdata_path: str = "/home/matteo/Desktop/VAMPIRE_TEST_RESULTS/A1/best test"  # results depot

#----------------------------------------------------------------------------------------------------------------------#

    def __init__(self, best_Fe, best_Ni, best_Co, trials, trial_length, random_scaling, signal_strength,random_input_locs,test_path):
        self.best_Fe = best_Fe
        self.best_Ni = best_Ni
        self.best_Co = best_Co
        self.materials = [self.best_Fe,self.best_Co, self.best_Ni]

        if trials is not None and trials > 0:
            self.trials = trials
        if trial_length is not None and trial_length > 0:
            self.trial_length = trial_length
        if random_scaling is not None:
            self.random_scaling = random_scaling
        if signal_strength is not None:
            self.signal_strength = signal_strength
        if random_input_locs is not None:
            self.random_input_locs = random_input_locs
        if os.path.exists(test_path):
            self.base_testdata_path = test_path + "/best test"

        os.mkdir(self.base_testdata_path)
        self.run_trials()

#----------------------------------------------------------------------------------------------------------------------#

    def run_trials(self):

        for trial in range(self.trials):

            print("#------------------------------------------------------------------------------#")
            print("#------------------------------------------------------------------------------#")
            print("#------------------------------------------------------------------------------#")
            print("#------------------------------------------------------------------------------#\n")
            self.NARMA_input, self.NARMA_output = GT(self.trial_length)
            print(f"WORKING ON TRIAL: {trial}\n")

            for material in self.materials:
                name = material["material:file"]
                print(f"WORKING ON MATERIAL: {name}\n")

                self.update_input_files(material)
                self.run_simulation()
                self.reservoir_computing()
                self.save_data(material,trial)

                if material["material:file"] == "Fe.mat":
                    self.Fe_list["NRMSE"].append(self.current_data["NRMSE"])
                    self.Fe_list["training_NRMSE"].append(self.current_data["training_NRMSE"])

                elif material["material:file"] == "Co.mat":
                    self.Co_list["NRMSE"].append(self.current_data["NRMSE"])
                    self.Co_list["training_NRMSE"].append(self.current_data["training_NRMSE"])

                elif material["material:file"] == "Ni.mat":
                    self.Ni_list["NRMSE"].append(self.current_data["NRMSE"])
                    self.Ni_list["training_NRMSE"].append(self.current_data["training_NRMSE"])

                print("DONE")
                print("#------------------------------------------------------------------------------#")
                print("#------------------------------------------------------------------------------#\n")

        self.make_box_plots()

#----------------------------------------------------------------------------------------------------------------------#

    def update_input_files(self, material):

        # calc how many cells for each dim, for constructing sourcefield.txt headers
        print(material)
        cells_perX = int((material["dimensions:system-size-x"] + 1) / material["cells:macro-cell-size"])
        cells_perY = int((material["dimensions:system-size-y"] + 1) / material["cells:macro-cell-size"])

        headers = make_headers(cells_perX, cells_perY)

        if self.random_scaling:
            scaled_input = self.NARMA_input.copy() * np.random.rand(self.trial_length, ) * material["field intensity input scaling"]
        else:
            scaled_input = self.NARMA_input.copy() * material["field intensity input scaling"]

        # rewrite sourcefield.txt
        write_sourcefield(output_path=self.base_workdir_path,
                  rows=scaled_input.shape[0],
                  timeseries=scaled_input,
                  columns=int(cells_perX * cells_perY),
                  all_same=True,
                  random_input_locs=self.random_input_locs,
                  headers=headers)

        new_height = scale_height(self.base_materials_path, material["material:file"], material["dimensions:system-size-z"])
        material["dimensions:system-size-z"] = new_height

        material_as_string = material.copy()

        material_as_string["dimensions:system-size-x"] = str(material["dimensions:system-size-x"]) + " !nm"
        material_as_string["dimensions:system-size-y"] = str(material["dimensions:system-size-y"]) + " !nm"
        material_as_string["dimensions:system-size-z"] = str(material["dimensions:system-size-z"]) + " !A"
        material_as_string["cells:macro-cell-size"] = str(material["cells:macro-cell-size"]) + " !nm"

        # copy material file to workdir, modify input file, change magnetic damping in .mat file
        smf(material_as_string["material:file"], self.base_materials_path,
            self.base_workdir_path)  # IMPORTANT THAT THIS GOES FIRST
        mvif(material_as_string.copy(), self.base_workdir_path)
        update_damping(self.base_workdir_path, material_as_string["intrinsic magnetic damping"])

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
        best_result, training_result, y, y_pred = train_ridge(self.base_workdir_path,self.NARMA_output, self.signal_strength)

        # None is returned if failed to fit model. occurs if sim outputs NaNs
        if best_result is not None:
            self.current_data = dict()
            self.current_data = {"y": y,
                                "y_pred":y_pred,
                                "training_NRMSE":training_result,
                                "NRMSE": best_result}

#----------------------------------------------------------------------------------------------------------------------#

    def save_data(self,material,trial):

        material_dir = self.base_testdata_path + "/" + material["material:file"][0:2]
        trial_dir = material_dir + "/" + str(trial)

        if not os.path.exists(material_dir):
            os.mkdir(material_dir)
        os.mkdir(trial_dir)

        plt.plot(np.arange(self.current_data['y_pred'].shape[0]), self.current_data['y'][:, 0], marker='o', markersize=1)
        plt.plot(np.arange(self.current_data['y_pred'].shape[0]), self.current_data['y_pred'][:, 0], marker='o', markersize=1)
        plt.xlabel('Time')  # X-axis label
        plt.ylabel('Magnitude')  # Y-axis label
        plt.title('Prediction')  # title of the plot
        plt.savefig(trial_dir + '/prediction task')
        plt.close()

        with open(trial_dir + '/accuracy_score.txt', "w") as file:

            file.writelines(material["material:file"] + "\n")
            for key, value in self.current_data.items():
                if key != 'y' and key != 'y_pred':
                    file.writelines(key + ": " + str(value) + "\n")
            file.close()

#----------------------------------------------------------------------------------------------------------------------#

    def make_box_plots(self):

        data = [self.Fe_list["NRMSE"],self.Co_list["NRMSE"], self.Ni_list["NRMSE"]]
        plt.title("NRMSEs of Best Runs")
        plt.ylabel("NRMSE")
        plt.boxplot(data, notch='True', patch_artist=True, labels=['Fe', 'Co', 'Ni'])
        plt.grid(visible=True)
        plt.savefig(self.base_testdata_path + "/box_plot.png")
        plt.show()
        plt.close()

#----------------------------------------------------------------------------------------------------------------------#

def main() -> None:

    best_co: dict = {"material:file": "Co.mat",
                                   "dimensions:system-size-x": 74,
                                   "dimensions:system-size-y": 74,
                                   "dimensions:system-size-z": 2.507,
                                   "cells:macro-cell-size": 5,
                                   "sim:temperature": 309.65,
                                   "intrinsic magnetic damping": 0.501,
                                   "field intensity input scaling": 0.1}

    best_fe: dict = {"material:file": "Fe.mat",
                     "dimensions:system-size-x": 74,
                     "dimensions:system-size-y": 74,
                     "dimensions:system-size-z": 2.866,
                     "cells:macro-cell-size": 5,
                     "sim:temperature": 309.65,
                     "intrinsic magnetic damping": 0.126,
                     "field intensity input scaling": 2}

    best_ni: dict = {"material:file": "Ni.mat",
                     "dimensions:system-size-x": 74,
                     "dimensions:system-size-y": 74,
                     "dimensions:system-size-z": 3.524,
                     "cells:macro-cell-size": 7.5,
                     "sim:temperature": 309.65,
                     "intrinsic magnetic damping": 0.126,
                     "field intensity input scaling": 1.05}

    signal_strength = 1e-13
    random_scaling = False
    input_length = 1000
    random_input_locs = False
    test_path = "/home/matteo/Desktop/VAMPIRE_TEST_RESULTS/C1"
    start = TrialBest(best_Co=best_co,
                      best_Fe=best_fe,
                      best_Ni=best_ni,
                      trials=5,
                      trial_length= input_length,
                      random_scaling= random_scaling,
                      random_input_locs=random_input_locs,
                      signal_strength=signal_strength,
                      test_path=test_path)

if __name__ == "__main__": main()
