import os

param_names = ["material:file", "dimensions:system-size-x", "dimensions:system-size-y",
               "dimensions:system-size-z", "cells:macro-cell-size", "sim:applied-field-strength",
               "sim:applied-field-unit-vector", "sim:temperature","intrinsic magnetic damping",
                "field intensity input scaling","iteration","training_NRMSE","NRMSE","signal_strength"]

dir="/home/matteo/Desktop/VAMPIRE_TEST_RESULTS/A1/Graphs"

if os.path.exists(dir):  # working directory where vampire binary is located
    with open(dir + "/best_iterations.txt", 'r') as f:
        data = f.readlines()
        f.close()

    # only considers params passed to create_plot_data
    parameters = dict()
    for name in param_names:
        parameters[name] = list()

    # extract all data, identified line by line as containing an "="
    for line in data:
        field = line.split(" = ")
        if len(field) == 1:  # skip empty lines. len = 1 by virtue of "\n"
            pass
        else:  # remove all chars which aren't number or material name
            value = field[1].strip("\n")
            value = value.replace("!A", "")
            value = value.replace("!T", "")
            value = value.replace(".mat", "")
            value = value.replace("!nm", "")
            value = value.replace(" ", "")
            parameters[field[0]].append(value)

    combo_list = list()
    for i in range(len(parameters["material:file"])):
        combo = dict()
        for index, key in enumerate(parameters.keys()):
            if key == "dimensions:system-size-z":
                combo[key] = parameters[key][i][:4]
            elif key == "NRMSE":
                combo[key] = "0"
            elif key == "training_NRMSE":
                combo[key] = "0"
            elif key == "iteration":
                combo[key] = "0"
            else:
                combo[key] = parameters[key][i]
        combo_list.append(combo)

    #print(combo_list)

    for index, combo in enumerate(combo_list):
        for index1, combo1 in enumerate(combo_list):
            if index1 != index:
                if combo == combo1:
                    print(combo)
                    print("\n\n")
                    print(combo1)
                    input()




