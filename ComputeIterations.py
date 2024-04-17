from random import randint
from ScaleGrid import scaleGrid
from ScaleHeight import scaleHeight

def computeIterations(workdir_path: str, input_file_parameters: dict, other_sweep_parameters: dict) -> int:

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

            new_height = scaleHeight(workdir_path, new_input_file_parameters["dimensions:system-size-z"])
            new_input_file_parameters["dimensions:system-size-z"] = new_height

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

    return len(tried_combos)