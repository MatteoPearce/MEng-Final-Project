
"""
Creates a sourcefield.txt file in specified path containing field components generated with uniform distribution
-1 < x < 1 of size row x col.
"""


import os
import sys
import warnings
from tqdm import tqdm
import random
import numpy as np

def filemaker(output_path: str,
              rows: int,
              columns: int,
              field_threshold: float = None,
              timeseries: np.ndarray = None,
              all_same:bool = False) -> None:

# ------------------------------------------------------------------ check inputs

    if columns is None or rows is None:
        raise ValueError('columns or rows cannot be None')

    if output_path is not None and os.path.exists(output_path):
        path_var = output_path + "/sourcefield.txt"
    else:
        path_var = "sourcefield.txt"
        warnings.warn("File path not specified/valid, output file will be created in current directory")

# ------------------------------------------------------------------ create 2D data string
    cell_num = int(columns**0.5)

    header1 = str()
    header2 = str()
    for i in range(1,cell_num+1):
        header1 = header1 + f"{i} "
        for j in range(1,cell_num+1):
            header2 = header2 + f"{i} "

    dummy = header1
    for i in range(cell_num-1):
        header1 = header1 + dummy

    header1 = header1 + "-2\n"
    header2 = header2 + "-1\n"

    data = str()

    if timeseries is not None:
        if all_same:
            for index, element in enumerate(timeseries):
                """
                row = np.repeat(element,columns)
                row = np.append(row,index)
                row = row.reshape((1, columns+1))
                """
                row = np.repeat(element, 5)

                row = np.append(row, index)
                row = row.reshape((1, columns + 1))
                if index == 0:
                    new_array = row
                else:
                    new_array = np.concatenate((new_array,row),axis=0)
                #print(new_array)
                #input()
        else:
            if timeseries.shape != (rows,columns):
                timeseries = timeseries.reshape((rows,columns))
        np.set_printoptions(threshold=sys.maxsize)
        data = np.array2string(new_array,  precision=4, separator=' ',max_line_width=columns**2)
        data.strip()
        data.lstrip(" ")
        data = data.replace("\n ","\n")
        data = data.replace("[","")
        data = data.replace("]", "")
        data = data.replace("      ", " ")
        data = data.replace("    ", " ")
        data = data.replace("   ", " ")
        data = data.replace("  "," ")

    else:

        column = str()

        for row in tqdm(range(rows)):
            for col in range(columns):

                val = round(random.uniform(-field_threshold, field_threshold), 4)

                if col == 0:
                    column = column + str(val)
                else:
                    column = column + " " + str(val)

            if row == 0:
                data = column +  " "  + str(row)
            else:
                data = data + "\n"  + column + " " + str(row)

            column = str()

    print(header1)
    print(header2)
    print(data)

# ------------------------------------------------------------------ write to file

    with open(path_var, "w") as file:
        file.writelines(header1)
        file.writelines(header2)
        file.writelines(str(data))

    print("\n#---------------------------------#")
    print("| SUCCESSFULLY WROTE SOURCE FILE  |")
    print("#---------------------------------#\n")


#filemaker("/home/matteo/Desktop/VAMPIRE_WORKDIR", 10, 100, 1)

