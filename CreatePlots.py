from collections import Counter
from itertools import product
import matplotlib.pyplot as plt
import numpy as np

def createPlotData(file_path: str = None, parameter_names: list = None, plot_all_graphs: bool = False, all_NRMSEs: bool = False) -> None:

    if file_path is not None:

        with open(file_path + "/best_iteration.txt", 'r') as f:
            data = f.readlines()
            f.close()

        parameters = dict()
        for name in parameter_names:
            parameters[name] = list()
        #parameters["iteration"] = list()
        #parameters["NRMSE"] = list()

        for line in data:

            field = line.split(" = ")
            if len(field) == 1:
                pass
            else:
                value = field[1].strip("\n")
                value = value.replace("!A","")
                value = value.replace("!T","")
                value = value.replace(".mat","")
                value = value.replace("!nm","")
                value = value.replace(" ","")
                parameters[field[0]].append(value)

        to_delete = list()
        for key in parameters.keys():
            counter = 0
            for i in range(len(parameters[key])-1):
                if parameters[key][i] != parameters[key][i+1]:
                    break
                else:
                    counter += 1

            if counter == len(parameters[key])-1:
                to_delete.append(key)

        for key in to_delete:
            parameters.pop(key)

        for key in parameters.keys():
            if key != "material:file":
                if key != "sim:applied-field-unit-vector":
                    for i in range(len(parameters[key])):
                        parameters[key][i] = float(parameters[key][i])
                else:
                    for i in range(len(parameters[key])):
                        if parameters[key][i][1] != '0':
                            parameters[key][i] = 1
                        elif parameters[key][i][3] != '0':
                            parameters[key][i] = 2
                        elif parameters[key][i][5] != '0':
                            parameters[key][i] = 3


        if plot_all_graphs:
            plotXY(file_path,parameters)
        plotTable(file_path, parameters, all_NRMSEs)
        plotMaterialComparison(file_path, parameters)
        #testBest(file_path,data)

#-----------------------------------------------------------------------------------------------------------------------

def plotXY(save_path: str = None, data: dict = None, variable_pair: tuple = None) -> None:

    data_copy = data.copy()
    labels = data["material:file"].copy()
    NRMSE = data["NRMSE"].copy()
    #data.pop("material:file")
    data_copy.pop("iteration")
    data_copy.pop("material:file")
    materials = list(Counter(labels).keys())
    #print(data)

    for material in materials:
        index_list = list()
        for index, entry in enumerate(labels):
            if material != entry:
                index_list.append(index)

        param_combos = list(product(data_copy.keys(), repeat=2))  # itertools.permutations does not allow repititions
        param_combos = list(np.unique(param_combos, axis=0))  # remove repeated events

        to_delete = list()
        for index,combo in enumerate(param_combos):
            if combo[0] != "NRMSE" and combo[1] != "NRMSE":
                to_delete.append(index)
            elif combo[0] == "NRMSE" and combo[1] == "NRMSE":
                to_delete.append(index)

            param_combos[index] = list(combo)

        for index in reversed(to_delete):
            param_combos.pop(index)

        for combo in param_combos:
            values1 = data_copy[combo[0]].copy()
            values2 = data_copy[combo[1]].copy()
            #print(combo, values1, values2)
            for index in reversed(index_list):
                    values1.pop(index)
                    values2.pop(index)

            plt.figure(figsize=(10, 5))
            plt.title(material)

            if combo[0] == 'NRMSE':

                plt.xlabel(combo[1])
                plt.ylabel(combo[0])
                plt.scatter(values2, values1)
            else:
                plt.xlabel(combo[0])
                plt.ylabel(combo[1])
                plt.scatter(values1, values2)

            plt.grid(visible=True)
            plt.show()

        #print(param_combos)

#-----------------------------------------------------------------------------------------------------------------------

def plotTable(save_path: str = None, data: dict = None, all_NRMSEs: bool = False) -> None:

    data_copy = data.copy()
    try:
        labels = data["material:file"].copy()
        data_copy.pop("material:file")
    except KeyError:
        for key in data.keys():
            array_length = len(data[key])
            break
        labels = list()
        for i in range(array_length):
            labels.append("Ag.mat") # INSERT NAME OF MATERIAL YOU TESTED IN ISOLATION

    materials = list(Counter(labels).keys())

    for material in materials:
        index_list = list()
        for index, entry in enumerate(labels):
            if material == entry:
                index_list.append(index)

        dict_to_plot = dict()
        for key in data_copy.keys():
            dict_to_plot[key] = list()
            for index in index_list:
                dict_to_plot[key].append(data_copy[key][index])

        for index, item in enumerate(dict_to_plot["NRMSE"]):
            dict_to_plot["NRMSE"][index] = round(item,4)

        for index, item in enumerate(dict_to_plot["training_NRMSE"]):
            dict_to_plot["training_NRMSE"][index] = round(item, 4)

        dict_to_plot["average_NRMSE"] = list()
        for i,j in zip(dict_to_plot["training_NRMSE"], dict_to_plot["NRMSE"]):
            dict_to_plot["average_NRMSE"].append( round((i * j)**0.5,4)  )

        NRMSE_list = ["training_NRMSE","NRMSE","average_NRMSE"]

        for index, name in enumerate(NRMSE_list):

            dummy_dict = dict_to_plot.copy()
            for key, value in dummy_dict.items():
                if key != name:
                    dict_to_plot[key] = [x for _, x in sorted(zip(dummy_dict[name], dummy_dict[key]))]

            dict_to_plot[name].sort()

            iterations = dict_to_plot["iteration"].copy()
            dummy_dict_to_plot = dict_to_plot.copy()
            dummy_dict_to_plot.pop("iteration")
            matrix = np.ndarray(len(dummy_dict_to_plot.keys()))

            for index,key in enumerate(dummy_dict_to_plot.keys()):

                row = np.array(dummy_dict_to_plot[key])
                row = row.reshape((len(index_list),1))# len(dict_to_plot.keys())))
                if index == 0:
                    matrix = row
                else:
                    matrix = np.concatenate((matrix,row), axis=1)

            valid_fields = dummy_dict_to_plot.keys()
            fig, ax = plt.subplots(figsize=(10,20))
            im = ax.imshow(matrix)

            # Show all ticks and label them with the respective list entries
            ax.set_xticks(np.arange(len(valid_fields)), labels=valid_fields)
            ax.set_yticks(np.arange(len(iterations)), labels=iterations)

            # Rotate the tick labels and set their alignment.
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                     rotation_mode="anchor")

            # Loop over data dimensions and create text annotations.
            for i in range(len(iterations)):
                for j in range(len(valid_fields)):

                    text = ax.text(j, i, str(matrix[i, j]),
                                   ha="center", va="center", color="w")

            #fig.colorbar(im, spacing='proportional',)
            ax.set_title(f"best iterations of {material} by {name}")
            ax.set_aspect('auto')

            fig.tight_layout()

            fig.savefig(save_path + "/" + material.strip(".mat") + "_" + name)
            plt.close()

            del fig, ax, im, matrix, iterations, valid_fields

        #print(matrix)

#-----------------------------------------------------------------------------------------------------------------------

def plotMaterialComparison(save_path: str = None, data: dict = None) -> None:

    try:
        labels = data["material:file"].copy()
    except KeyError:
        for key in data.keys():
            array_length = len(data[key])
            break
        labels = list()
        for i in range(array_length):
            labels.append("Ag.mat")  # INSERT NAME OF MATERIAL YOU TESTED IN ISOLATION

    NRMSE = data["NRMSE"].copy()
    training_NRMSE = data["training_NRMSE"].copy()
    materials = list(Counter(labels).keys())
    values = { "training_NRMSE" : list(),
               "NRMSE" : list(),
               "average_NRMSE" : list()
             }

    average_NRMSE = list()
    for i, j in zip(training_NRMSE, NRMSE):
        average_NRMSE.append(round((i * j) ** 0.5, 4))

    for material in materials:
        dict_to_plot = dict()
        index_list = list()
        for index, entry in enumerate(labels):
            if material == entry:
                index_list.append(index)

        NRMSE_current_mat = list()
        training_NRMSE_current_mat = list()
        average_NRMSE_current_mat = list()
        min_NRMSE = None
        for index in index_list:
            NRMSE_current_mat.append(NRMSE[index])
            training_NRMSE_current_mat.append(training_NRMSE[index])
            average_NRMSE_current_mat.append(average_NRMSE[index])
        min_NRMSE = min(NRMSE_current_mat.copy())
        min_training_NRMSE = min(training_NRMSE_current_mat)
        min_average_NRMSE = min(average_NRMSE_current_mat)

        values["training_NRMSE"].append(round(min_training_NRMSE,4))
        values["NRMSE"].append(round(min_NRMSE,4))
        values["average_NRMSE"].append(round(min_average_NRMSE,4))

    x = np.arange(len(materials))  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained')

    for attribute, measurement in values.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('error')
    ax.set_title('best NRMSEs by material')
    ax.set_xticks(x + width, materials)
    ax.legend(loc='upper left', ncols=3)
    ax.set_ylim(0, 0.4)

    plt.grid(visible=True)
    plt.savefig(save_path + "/materials_comparison")

    """plt.figure(figsize=(10, 5))
    plt.title("materials comparison")
    plt.xlabel("materials")
    plt.ylabel("NRMSE")
    plt.scatter(materials, values)
    plt.grid(visible=True)
    plt.savefig(save_path + "/materials_comparison")
    plt.close()
    #plt.show()"""

# -----------------------------------------------------------------------------------------------------------------------

def testBest(test_data_path: str = None,data:dict = None):

    best_results = { "training_NRMSE" : list(),
                     "NRMSE" : list(),
                     "material" : list()
                   }

    for line in data:

        if "training_NRMSE" in line:
            best_results["training_NRMSE"].append(float(line.split(" = ")[1]))
        if "NRMSE" in line:
            best_results["NRMSE"].append(float(line.split(" = ")[1]))
        if "material:file" in line:
            best_results["material"].append(line.split(" = ")[1].strip(".mat\n"))

    NRMSE_list = ["training_NRMSE", "NRMSE"]

    for index, name in enumerate(NRMSE_list):

        dummy_dict = best_results.copy()
        for key, value in dummy_dict.items():
            if key != name:
                best_results[key] = [x for _, x in sorted(zip(dummy_dict[name], dummy_dict[key]))]

        best_results[name].sort()

        print(best_results)
        input()

#-----------------------------------------------------------------------------------------------------------------------

param_names = ["material:file", "dimensions:system-size-x", "dimensions:system-size-y",
               "dimensions:system-size-z", "cells:macro-cell-size", "sim:applied-field-strength",
               "sim:applied-field-unit-vector", "sim:temperature","intrinsic magnetic damping",
                "field intensity input scaling","iteration","training_NRMSE","NRMSE"]
createPlotData( "/home/matteo/Desktop/VAMPIRE_TEST_RESULTS",param_names,all_NRMSEs=True)