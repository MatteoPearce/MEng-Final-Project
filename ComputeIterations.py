from random import randint
from ScaleGrid import scale_grid
from ScaleHeight import scale_height

"""
CHECK NUMBER OF UNIQUE PARAMETER COMBINATIONS

Code copied from MaterialEvolution class method "select_parameters" and tweaked. 

Tries a combo, checks a list of already tried combos, if not there add to list. if 10k combinations in a row aren't
unique, quit and return number of combos. 
"""

def compute_iterations(workdir_path: str, input_file_parameters: dict, other_sweep_parameters: dict) -> int:

    tried_combos = list() # list of unique combos
    searching_combos = True # False when no unique combos found
    attempts = 0 # counter

    while searching_combos:

            # will populate with randomly generated selection of params
            new_input_file_parameters = dict()
            new_other_sweep_parameters = dict()
            all_sweep_parameters = dict()  # combo of input file and other sweep params

            for key,value in input_file_parameters.items():
                number = randint(0,len(value)-1) # populate with random values from available params
                new_input_file_parameters[key] = value[number]

            # check that height is multiple of unit cell
            new_height = scale_height(workdir_path,new_input_file_parameters["material:file"], new_input_file_parameters["dimensions:system-size-z"])
            new_input_file_parameters["dimensions:system-size-z"] = new_height

            # check that x and y dims are multiple of cell length
            new_x, new_y, new_grid = scale_grid(x_dims=input_file_parameters["dimensions:system-size-x"],
                                               y_dims=input_file_parameters["dimensions:system-size-y"],
                                               cell_dim=input_file_parameters["cells:macro-cell-size"])

            new_input_file_parameters["dimensions:system-size-x"] = new_x
            new_input_file_parameters["dimensions:system-size-y"] = new_y
            new_input_file_parameters["cells:macro-cell-size"] = new_grid

            # will populate with randomly generated selection of params
            for key, value in other_sweep_parameters.items():
                number = randint(0, len(value) - 1)
                new_other_sweep_parameters[key] = value[number]

            all_sweep_parameters.update(new_input_file_parameters)
            all_sweep_parameters.update(new_other_sweep_parameters)

            if len(tried_combos) == 0: # if first iteration, append - must be unique
                unique = True
            else:
                unique = True
                for combo in tried_combos: # is unique until equivalent found
                    if combo == all_sweep_parameters:
                        unique = False
                        break

            if unique:
                tried_combos.append(all_sweep_parameters.copy())
                attempts = 0
            else:
                attempts += 1

            if attempts >= 10000: #10k is arbitrary, might need to be more if very large search
                searching_combos = False

    return len(tried_combos)