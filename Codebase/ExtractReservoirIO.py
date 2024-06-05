import os
import numpy as np

"""
GRABS sourcefield.txt AND reservoir_output.txt AND CONVERTS TO NUMPY ARRAY
"""

def extract_reservoir_IO(file_path1: str,file_path2: str) -> np.ndarray:

    # allows the files to be saved in different locations
    paths = [file_path1, file_path2]
    output_arrays = list()

    if os.path.exists(file_path1) and os.path.exists(file_path2):

        for file_path in paths:

            with open(file_path, "r") as file:
                cell_num = len(file.readline().split(" "))-1 # sourcefield contains timestep label, reservoir_output an extra \n
                data = file.readlines()
                file.close()

            for index, line in enumerate(data):

                dummy_list = line.strip().split(" ")

                # ensure only field strength data captured
                if len(dummy_list) > cell_num:
                    dummy_list.pop(-1)

                # convert current line to numpy array
                dummy_array = np.asarray(dummy_list,dtype=np.float128)
                dummy_array = dummy_array.reshape((1,len(dummy_list)))

                # stack lines of data on top of each other row-wise, acheiving matrix of size: timesteps x cells
                if index == 0:
                    numpy_array = dummy_array
                else:
                    numpy_array = np.concatenate((numpy_array,dummy_array),axis=0)

            output_arrays.append(numpy_array)

        return output_arrays

    else:
        raise FileNotFoundError("IO NOT FOUND")
