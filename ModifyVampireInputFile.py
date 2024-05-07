

"""
Compatible with VAMPIRE 6 input .txt files. Receives parameter names and new values
with which to update VAMPIRE input file for each iteration of parameter sweep.
"""
import os
import warnings

def modifyVampireInputFile(new_vals: dict = None, file_path : str = None) -> None:

#------------------------------------------------------------------ check inputs

    if new_vals is None:
        raise ValueError('dictionary cannot be None')

    if file_path is not None and os.path.exists(file_path):
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
            if line[0] == '#':
                pass
            else:
                as_list = line.split("\n")
                split_lines.append(as_list[0])

        for line in split_lines:
            as_list = line.replace(" ","").split("=")
            if len(as_list) == 2:
                modifiable_params.append(as_list)

    modifiable_params = dict(modifiable_params)
    file.close()

#------------------------------------------------------------------ extract unit cell info

    for file in os.listdir(file_path):
        filename = os.fsdecode(file)
        if filename.endswith(".mat"):
            with open(os.path.join(file_path, file), "r") as f:
                material_data = f.readlines()
                f.close()
            break

    cell_structure = material_data[0].split(" = ")[1].strip("\n")
    cell_size = material_data[1].split(" = ")[1].strip("\n")

    cell_info = {"create:crystal-structure" : cell_structure,
                 "dimensions:unit-cell-size" : cell_size}

    new_vals.update(cell_info)

#------------------------------------------------------------------ modify parameters

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

#new_vals = {"sim:applied-field-unit-vector": (0,1,0)}
#modifyVampireInputFile(new_vals, "/home/matteo/Desktop/VAMPIRE_WORKDIR")