import os
import warnings

"""
Compatible with VAMPIRE 5.0.0 input.txt files. Receives parameter names and new values
with which to update VAMPIRE input file for each iteration of parameter sweep.
"""

def modify_vampire_input(new_vals: dict = None, file_path : str = None) -> None:

#------------------------------------------------------------------ check inputs

    if new_vals is None:
        raise ValueError('dictionary cannot be None')

    if os.path.exists(file_path):
        if "input" in file_path:
            VAMPIRE_input = file_path
        else:
            VAMPIRE_input = file_path + "/input"
    else:
        raise Exception("File path is not a valid input file")

#------------------------------------------------------------------ extract modifiable parameters

    with open(VAMPIRE_input, "r") as file:

        initial_data = file.readlines()
        split_lines = list()
        modifiable_params = list()

        for line in initial_data:
            if line[0] == '#': # hash is a comment in vampire files.
                pass
            else:
                as_list = line.split("\n") # populate list, each line an entry
                split_lines.append(as_list[0])

        for line in split_lines:
            as_list = line.replace(" ","").split("=") # remove whitespace and separate into name and value
            if len(as_list) == 2: # if not split, it's not a parameter
                modifiable_params.append(as_list)

    modifiable_params = dict(modifiable_params)
    file.close()

#------------------------------------------------------------------ extract unit cell info

    # grab .mat file
    for file in os.listdir(file_path):
        filename = os.fsdecode(file)
        if filename.endswith(".mat"):
            with open(os.path.join(file_path, file), "r") as f:
                material_data = f.readlines()
                f.close()
            break

    # cell structure and unit cell size are first two comments
    cell_structure = material_data[0].split(" = ")[1].strip("\n")
    cell_size = material_data[1].split(" = ")[1].strip("\n")

    cell_info = {"create:crystal-structure" : cell_structure,
                 "dimensions:unit-cell-size" : cell_size}

    new_vals.update(cell_info)

#------------------------------------------------------------------ modify parameters

    # only modifiable parameters should be updated, if length increases then something has gone wrong
    len_check = len(modifiable_params.items())
    modifiable_params.update(new_vals)

    if len_check < len(modifiable_params.items()):
        warnings.warn('YOU HAVE ADDED AN EXTRA PARAMETER')

#------------------------------------------------------------------ write to input file

    for key in modifiable_params.keys():
        for index,line in enumerate(initial_data):
            if (key + " ") in line:
                initial_data[index] = str(key + " = " + str(modifiable_params[key]).strip(")(") + "\n")
                break

    with open(VAMPIRE_input, "w") as file:
        file.writelines(initial_data)
        file.close()

    print("\n#---------------------------------#")
    print("| SUCCESSFULLY UPDATED INPUT FILE |")
    print("#---------------------------------#\n")
    print(f"VALUES UPDATED:\n\n{new_vals}")
    print("\n#--------------------------------------------------------------#")