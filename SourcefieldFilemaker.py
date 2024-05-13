import os
import sys
import warnings
import random
import numpy as np

"""
CREATES THE sourcefield.txt FILE.

Supports several construction methods. For use with MaterialEvolution class, pass timeseries and headers. 

To generate random data, leave these as None and choose rows x columns where rows = timesteps and columns = cells. 
field_threshold sets the bounds for which random numbers will be generated, x = random [ -field_threshold ; +field_threshold ].
If all_same = True, only 1 random number is generated and all values are set to this. 

If being used independently of MaterialEvolution class, the film must be square and columns must have an integer 
square root or the file won't be generated properly. 
"""

def write_sourcefield(output_path: str,
              rows: int,
              columns: int,
              field_threshold: float = None,
              timeseries: np.ndarray = None,
              all_same:bool = False,
              headers: list = None) -> None:

# ------------------------------------------------------------------ check inputs

    if columns is None or rows is None:
        raise ValueError('columns or rows cannot be None')

    if os.path.exists(output_path):
        path_var = output_path + "/sourcefield.txt"
    else:
        path_var = "sourcefield.txt"
        warnings.warn("File path not specified/valid, output file will be created in current directory")

# ------------------------------------------------------------------ create 2D data


    if headers is not None:
        header1 = headers[0]
        header2 = headers[1]

    # unlike ScaleGrid.py, only uses cell_num, therefore incompatible with rectangular films
    else:
        cell_num = int(columns ** 0.5)
        header1 = str()
        header2 = str()

        for i in range(1,cell_num+1):
            header2 = header2 + f"{i} "
            for j in range(1,cell_num+1):
                header1 = header1 + f"{i} "

        dummy = header2
        for i in range(cell_num-1):
            header2 = header2 + dummy

    header1 = header1 + "-2\n"
    header2 = header2 + "-1\n"

    data = str()

    # in random search all_same should be True
    if timeseries is not None:
        if all_same:
            for index, element in enumerate(timeseries):

                row = np.repeat(element,columns)
                row = np.append(row,index)
                row = row.reshape((1, columns+1)) # extra column for timestep label ****************************

                if index == 0:
                    new_array = row
                else:
                    new_array = np.concatenate((new_array,row),axis=0)

        else:
            if timeseries.shape != (rows,columns):
                timeseries = timeseries.reshape((rows,columns))

        np.set_printoptions(threshold=sys.maxsize) # improves legibility when debugging or testing
        data = np.array2string(new_array,  precision=4, separator=' ',max_line_width=columns**2)
        data.strip()

        # remove all possible whitespace and list brackets
        data.lstrip(" ")
        data = data.replace("\n ","\n")
        data = data.replace("[","")
        data = data.replace("]", "")
        data = data.replace("      ", " ")
        data = data.replace("    ", " ")
        data = data.replace("   ", " ")
        data = data.replace("  "," ")

    # random numbers will be generated
    else:
        column = str()
        for row in range(rows):
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

# ------------------------------------------------------------------ write to file

    with open(path_var, "w") as file:
        file.writelines(header1)
        file.writelines(header2)
        file.writelines(str(data))

    print("\n#---------------------------------#")
    print("| SUCCESSFULLY WROTE SOURCE FILE  |")
    print("#---------------------------------#\n")


