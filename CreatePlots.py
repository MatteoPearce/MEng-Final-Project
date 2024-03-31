from collections import Counter
from itertools import product
import matplotlib.pyplot as plt
import numpy as np

def createPlotData(file_path: str = None, parameter_names: list = None) -> None:

    if file_path is not None:

        with open(file_path + "/best_iteration.txt", 'r') as f:
            data = f.readlines()
            f.close()

        parameters = dict()
        for name in parameter_names:
            parameters[name] = list()
        parameters["iteration"] = list()
        parameters["NRMSE"] = list()

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

        #print(parameters)
        #plotXY(file_path,parameters)
        plotHeatmap(file_path, parameters)

#-----------------------------------------------------------------------------------------------------------------------

def plotXY(save_path: str = None, data: dict = None) -> None:

    labels = data["material:file"]
    NRMSE = data["NRMSE"]
    data.pop("material:file")
    data.pop("iteration")
    materials = list(Counter(labels).keys())
    print(data)

    for material in materials:
        index_list = list()
        for index, entry in enumerate(labels):
            if material != entry:
                index_list.append(index)

        param_combos = list(product(data.keys(), repeat=2))  # itertools.permutations does not allow repititions
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
            values1 = data[combo[0]].copy()
            values2 = data[combo[1]].copy()
            print(combo, values1, values2)
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

        print(param_combos)

#-----------------------------------------------------------------------------------------------------------------------

def plotHeatmap(save_path: str = None, data: dict = None) -> None:

    labels = data["material:file"]
    data.pop("material:file")

    materials = list(Counter(labels).keys())

    for material in materials:
        index_list = list()
        for index, entry in enumerate(labels):
            if material == entry:
                index_list.append(index)

        dict_to_plot = dict()
        for key in data.keys():
            dict_to_plot[key] = list()
            for index in index_list:
                dict_to_plot[key].append(data[key][index])

        iterations = dict_to_plot["iteration"].copy()
        dict_to_plot.pop("iteration")
        matrix = np.ndarray(shape=(17,))#len(dict_to_plot.keys())))

        for index, item in enumerate(dict_to_plot["NRMSE"]):
            dict_to_plot["NRMSE"][index] = round(item,4)

        for index,key in enumerate(dict_to_plot.keys()):

            row = np.array(dict_to_plot[key])
            row = row.reshape((len(index_list),1))# len(dict_to_plot.keys())))
            if index == 0:
                matrix = row
            else:
                matrix = np.concatenate((matrix,row), axis=1)

        valid_fields = dict_to_plot.keys()
        fig, ax = plt.subplots()
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
                #print(i)
                text = ax.text(j, i, str(matrix[i, j]),
                               ha="center", va="center", color="w")

        fig.colorbar(im, spacing='proportional')
        ax.set_title(f"best iterations of {material}")
        ax.set_aspect('auto')

        fig.tight_layout()
        plt.show()
        #input()
        fig.savefig(save_path + "/" + material.strip(".mat"))
        plt.close()

        del fig, ax, im, matrix, iterations, valid_fields

        #print(matrix)

#-----------------------------------------------------------------------------------------------------------------------

param_names = ["material:file", "dimensions:system-size-x", "dimensions:system-size-y",
               "dimensions:system-size-z", "cells:macro-cell-size", "sim:applied-field-strength",
               "sim:applied-field-unit-vector", "sim:temperature"]
createPlotData("/home/matteo/Desktop/VAMPIRE_TEST_RESULTS",param_names)