from random import randint
from ScaleGrid import scaleGrid
import numpy as np
"""other_sweep_parameters: dict = { "intrinsic magnetic damping" : [0.001,0.01,0.1,0.5,1],
                                   "field intensity input scaling": [-2,-1.5,-1,-0.5,0.5,1,1.5,2]}

input_file_parameters: dict = { "material:file" : ["Co.mat","Fe.mat","Ni.mat"],#
                              "dimensions:system-size-x" : [49,99],#149,199],
                              "dimensions:system-size-y" : [49,99],#,99,149,199],
                              "dimensions:system-size-z" : [0.1],#np.arange(0.1,1,0.1),
                              "cells:macro-cell-size" : [5,10,20],#,10,15,20],
                              "sim:applied-field-strength" : [0],#,1e-24,1e-12,1e-6],
                              "sim:applied-field-unit-vector": [(0,0,1)],#,(0,1,0),(1,0,0)],
                              "sim:temperature" : [0]} #MAKE SURE DEFAULT IS ALWAYS INDEX 0"""

"""input_file_parameters: dict = { "material:file" : ["Co.mat","Fe.mat","Ni.mat"],#"Ag.mat"],
                              "dimensions:system-size-x" : [49],
                              "dimensions:system-size-y" : [49],
                              "dimensions:system-size-z" : [1,2,3,4,5,6],#np.arange(0.1,1,0.1),
                              "cells:macro-cell-size" : [5],
                              "sim:applied-field-strength" : [0],#,"1e-24 !T","1e-12 !T","1e-6 !T"],
                              "sim:applied-field-unit-vector": [(0,0,1)],#,(0,1,0),(1,0,0)],
                              "sim:temperature" : [309.65]} #MAKE SURE DEFAULT IS ALWAYS INDEX 0

other_sweep_parameters: dict = { "intrinsic magnetic damping" : [0.001,0.01,0.1,0.5,1],
                                   "field intensity input scaling": [-2,-1.5,-1,-0.5,0.5,1,1.5,2]}"""

input_file_parameters: dict = { "material:file" : ["Co.mat","Fe.mat","Ni.mat","Ag.mat","Am.mat","At.mat","Al.mat","Ax.mat"],
                              "dimensions:system-size-x" : np.arange(99,549,50),
                              "dimensions:system-size-y" : np.arange(99,549,50),
                              "dimensions:system-size-z" : np.arange(1,31,1),#np.arange(0.1,1,0.1),
                              "cells:macro-cell-size" : np.arange(5,55,5),
                              "sim:applied-field-strength" : [0],#,"1e-24 !T","1e-12 !T","1e-6 !T"],
                              "sim:applied-field-unit-vector": [(0,0,1)],#,(0,1,0),(1,0,0)],
                              "sim:temperature" : [309.65]} #MAKE SURE DEFAULT IS ALWAYS INDEX 0

other_sweep_parameters: dict = { "intrinsic magnetic damping" : np.arange(0.001,1.051,0.05),
                                   "field intensity input scaling": [-2,-1.5,-1,-0.5,0.5,1,1.5,2]}



all_sweep_parameters: dict = dict()
new_input_file_parameters: dict = dict()
new_other_sweep_parameters: dict = dict()
tried_combos: list = list()

searching_combo = True
attempts = 0

while searching_combo:

        new_input_file_parameters = {}
        for key,value in input_file_parameters.items():
            if (key == "dimensions:system-size-x" or key == "dimensions:system-size-y"):
                number = 0
            elif (key == "cells:macro-cell-size"):
                number = 0
            elif (key == "sim:temperature"):
                number = 0
            else:
                number = randint(0,len(value)-1)

            new_input_file_parameters[key] = value[number]

        if True:

            new_x, new_y, new_grid = scaleGrid(x_dims=input_file_parameters["dimensions:system-size-x"],
                                               y_dims=input_file_parameters["dimensions:system-size-y"],
                                               cell_dim=input_file_parameters["cells:macro-cell-size"],
                                               save_path=None,
                                               timeseries=None)

            new_input_file_parameters["dimensions:system-size-x"] = new_x
            new_input_file_parameters["dimensions:system-size-y"] = new_y
            new_input_file_parameters["cells:macro-cell-size"] = new_grid

        for key, value in other_sweep_parameters.items():
            number = randint(0, len(value) - 1)
            new_other_sweep_parameters[key] = value[number]

        all_sweep_parameters.update(new_input_file_parameters)
        all_sweep_parameters.update(new_other_sweep_parameters)

        if len(tried_combos) == 0:
            unique = True
        else:
            unique = True
            for combo in tried_combos:
                if combo == all_sweep_parameters:
                    unique = False
                    break

        if unique:
            tried_combos.append(all_sweep_parameters.copy())
            #searching_combo = False


        if attempts >= 100000:
            searching_combo = False
            simulation_end = True

        attempts += 1

print(len(tried_combos))