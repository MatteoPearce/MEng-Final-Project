from collections import Counter
from itertools import product
import matplotlib.pyplot as plt
import numpy as np
import os

"""
USES best_iterations.txt TO CREATE PLOTS OF RANDOM SEARCH RESULTS

create_plot_data extracts the data from best_iterations.txt and converts strings to floats, before passing to plotter functions.

3 types of plot available:

    XY - goes through every combination of explored params and creates cartesian plot. Currently only showed in IDE and not saved as not useful.
    Table - parameters on X axis, best iteration number on Y axis, arranged in order of best NRMSE for untested data or tested data.
    Material Comparison - shows comparison of best run per material via bar plots.
    
The params to plot are passed to create_plot_data, so that plots can be easily customised.

contains compatibility for static applied field with unit vector. converts tuple of components to numerical:

    (1,0,0) -> 1
    (0,1,0) -> 2
    (0,0,1) -> 3
    
only normal directions allowed. Only makes sense if Vampire input file contains non-zero applied file. 
"""

def create_plot_data(test_path: str = None, parameter_names: list = None, plot_all_graphs: bool = False, all_NRMSEs: bool = False) -> None:

    if os.path.exists(test_path):  # working directory where vampire binary is located
        with open(test_path + "/best_iterations.txt", 'r') as f:
            data = f.readlines()
            f.close()

        # only considers params passed to create_plot_data
        parameters = dict()
        for name in parameter_names:
            parameters[name] = list()

        # extract all data, identified line by line as containing an "="
        for line in data:
            field = line.split(" = ")
            if len(field) == 1: # skip empty lines. len = 1 by virtue of "\n"
                pass
            else: # remove all chars which aren't number or material name
                value = field[1].strip("\n")
                value = value.replace("!A","")
                value = value.replace("!T","")
                value = value.replace(".mat","")
                value = value.replace("!nm","")
                value = value.replace(" ","")
                parameters[field[0]].append(value)

        # remove params which have not been varied in this random search
        to_delete = list()
        for key in parameters.keys():
            counter = 0
            for i in range(len(parameters[key])-1):
                if key != "material:file": # without this single materials can't be plotted
                    if parameters[key][i] != parameters[key][i+1]: # if even 1 difference between two iterations, keep param
                        break
                    else:
                        counter += 1 # counter increments every time two param data are the same

            if counter == len(parameters[key])-1: # if counter == length of data for one param -> all same
                to_delete.append(key) # delete that param

        for key in to_delete:
            parameters.pop(key)

        # ignoring material name, convert str to float
        for key in parameters.keys():
            if key != "material:file":
                if key != "sim:applied-field-unit-vector":
                    for i in range(len(parameters[key])):
                        parameters[key][i] = float(parameters[key][i])
                else: # only relevant if static field applied and part of search.
                    for i in range(len(parameters[key])): # field vector converted to 1,2,3 so can be treated mathematically
                        if parameters[key][i][1] != '0':
                            parameters[key][i] = 1
                        elif parameters[key][i][3] != '0':
                            parameters[key][i] = 2
                        elif parameters[key][i][5] != '0':
                            parameters[key][i] = 3


        if plot_all_graphs: # XY plots can be hard to read, not plotted as standard
            plot_XY(test_path,parameters)
        plot_table(test_path, parameters)
        plot_material_comparison(test_path, parameters)

#-----------------------------------------------------------------------------------------------------------------------

def plot_XY(save_path: str = None, data: dict = None, variable_pair: tuple = None) -> None:

    data_copy = data.copy()
    data_copy.pop("iteration") # iteration not useful for XY plots
    data_copy.pop("material:file") # materials tracked in separate variable

    labels = data["material:file"].copy()
    materials = list(Counter(labels).keys()) # extracts each material name

    # plots XY of every param combination, one material at a time
    for material in materials:
        index_list = list()
        # only saves data inherent to current material
        for index, entry in enumerate(labels):
            if material != entry:
                index_list.append(index)

        # cartesian product yields all combos
        param_combos = list(product(data_copy.keys(), repeat=2))  # itertools.permutations does not allow repititions
        param_combos = list(np.unique(param_combos, axis=0))  # remove repeated events

        # remove all combos which don't contain NRMSE or are only NRMSE
        to_delete = list()
        for index,combo in enumerate(param_combos):
            if combo[0] != "NRMSE" and combo[1] != "NRMSE":
                to_delete.append(index)
            elif combo[0] == "NRMSE" and combo[1] == "NRMSE":
                to_delete.append(index)

            param_combos[index] = list(combo) # convert tuple to list

        # # remove all combos which don't contain NRMSE or are only NRMSE
        for index in reversed(to_delete):
            param_combos.pop(index)

        # extract values for plot
        for combo in param_combos:
            values1 = data_copy[combo[0]].copy()
            values2 = data_copy[combo[1]].copy()

            # remove data from different material
            for index in reversed(index_list):
                    values1.pop(index)
                    values2.pop(index)

            plt.figure(figsize=(10, 5))
            plt.title(material)

            # makes sure NRMSE is always on the Y axis
            if combo[0] == 'NRMSE':

                plt.xlabel(combo[1])
                plt.ylabel(combo[0])
                plt.scatter(values2, values1)
            else:
                plt.xlabel(combo[0])
                plt.ylabel(combo[1])
                plt.scatter(values1, values2)

            plt.grid(visible=True)
            plt.show() # for now doesn't save plots as I Haven't found them useful

#-----------------------------------------------------------------------------------------------------------------------

def plot_table(save_path: str = None, data: dict = None, bool = False) -> None:

    data_copy = data.copy()
    data_copy.pop("material:file") # materials tracked in separate variable

    labels = data["material:file"].copy()
    materials = list(Counter(labels).keys()) # extracts each material name

    # plots Table of best runs of every material
    for material in materials:
        index_list = list()
        # only saves data inherent to current material
        for index, entry in enumerate(labels):
            if material == entry:
                index_list.append(index)

        # adds all data for current material to a dict
        dict_to_plot = dict()
        for key in data_copy.keys():
            dict_to_plot[key] = list()
            for index in index_list:
                dict_to_plot[key].append(data_copy[key][index])

        # rounds NRMSE values to 4 decimal places
        for index, item in enumerate(dict_to_plot["NRMSE"]):
            dict_to_plot["NRMSE"][index] = round(item,4)

        for index, item in enumerate(dict_to_plot["training_NRMSE"]):
            dict_to_plot["training_NRMSE"][index] = round(item, 4)

        # one table for NRMSE on unseen data and one for NRMSE on training data
        NRMSE_list = ["training_NRMSE","NRMSE"]
        for index, name in enumerate(NRMSE_list):

            # IMPORTANT - sorts all dict items to be in order of ascending NRMSE
            dummy_dict = dict_to_plot.copy()
            for key, value in dummy_dict.items():
                if key != name:
                    # use NRMSE as template and sort accordingly
                    dict_to_plot[key] = [x for _, x in sorted(zip(dummy_dict[name], dummy_dict[key]))]

            # after sorting all other items, sort NRMSE
            dict_to_plot[name].sort()
            dummy_dict_to_plot = dict()

            for index, key in enumerate(dict_to_plot.keys()):
                dummy_dict_to_plot[key] = dict_to_plot[key][:10]

            # iteration number is the row label and saved in separate list
            iterations = dummy_dict_to_plot["iteration"].copy()
            #dummy_dict_to_plot = dict_to_plot.copy()
            dummy_dict_to_plot.pop("iteration")

            # create table in the form of a matrix
            matrix = np.ndarray(len(dummy_dict_to_plot.keys()))

            # reshape into rows and columns of size: N_datapoints x params
            for index,key in enumerate(dummy_dict_to_plot.keys()):
                row = np.array(dummy_dict_to_plot[key])
                row = row.reshape((10,1))
                if index == 0:
                    matrix = row
                else:
                    matrix = np.concatenate((matrix,row), axis=1)

            valid_fields = dummy_dict_to_plot.keys() # names of params
            fig, ax = plt.subplots(figsize=(10,20))
            im = ax.imshow(matrix)

            # Show all ticks and label them with the respective list entries
            ax.set_xticks(np.arange(len(valid_fields)), labels=valid_fields)
            ax.set_yticks(np.arange(len(iterations)), labels=iterations)

            # Rotate the tick labels and set their alignment.
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                     rotation_mode="anchor") # rotate names to fit

            # Loop over data dimensions and create text annotations.
            for i in range(10):
                for j in range(len(valid_fields)):
                    text = ax.text(j, i, str(matrix[i, j]),
                                   ha="center", va="center", color="w")

            ax.set_title(f"best iterations of {material} by {name}")
            ax.set_aspect('auto')
            fig.tight_layout()
            fig.savefig(save_path + "/" + material.strip(".mat") + "_" + name)
            plt.close()

            del fig, ax, im, matrix, iterations, valid_fields # create anew per material

#-----------------------------------------------------------------------------------------------------------------------

def plot_material_comparison(save_path: str = None, data: dict = None) -> None:

    # the only data needed is NRMSE and material name
    NRMSE = data["NRMSE"].copy()
    training_NRMSE = data["training_NRMSE"].copy()

    labels = data["material:file"].copy()
    materials = list(Counter(labels).keys())  # extracts each material name

    values = { "training_NRMSE" : list(),
               "NRMSE" : list()
             }

    # for every material, extract all NRMSE data, find lowest and append to values dict
    for material in materials:
        index_list = list()
        for index, entry in enumerate(labels):
            if material == entry:
                index_list.append(index)

        NRMSE_current_mat = list()
        training_NRMSE_current_mat = list()

        for index in index_list:
            NRMSE_current_mat.append(NRMSE[index])
            training_NRMSE_current_mat.append(training_NRMSE[index])

        min_NRMSE = min(NRMSE_current_mat.copy())
        min_training_NRMSE = min(training_NRMSE_current_mat)

        # rounds NRMSE values to 4 decimal places
        values["training_NRMSE"].append(round(min_training_NRMSE,4))
        values["NRMSE"].append(round(min_NRMSE,4))

    x = np.arange(len(materials))  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0

    # make bar plots
    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in values.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # add text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('error')
    ax.set_title('best NRMSEs by material')
    ax.set_xticks(x + width, materials)
    ax.legend(loc='upper left', ncols=3)
    ax.set_ylim(0, 20)

    plt.grid(visible=True)
    plt.savefig(save_path + "/materials_comparison")

#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#

param_names = ["material:file", "dimensions:system-size-x", "dimensions:system-size-y",
               "dimensions:system-size-z", "cells:macro-cell-size", "sim:applied-field-strength",
               "sim:applied-field-unit-vector", "sim:temperature","intrinsic magnetic damping",
                "field intensity input scaling","iteration","training_NRMSE","NRMSE","signal_strength"]

dir = "/home/matteo/Desktop/VAMPIRE_TEST_RESULTS/"
dir = "/home/matteo/Downloads/testMEng/"
create_plot_data(dir,param_names)