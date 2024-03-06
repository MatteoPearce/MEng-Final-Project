

"""
Compatible with VAMPIRE 6 input .txt files. Receives parameter names and new values
with which to update VAMPIRE input file for each iteration of parameter sweep.
"""
import os
import pandas as pd

def modifyVampireInputFile(new_vals: dict,file_path : str) -> None:

    # open input.txt as a pandas dataframe. accepts full path as well as directory.

    if file_path is not None and os.path.exists(file_path):
        if "input.txt" in file_path:
            VAMPIRE_input = pd.read_table(file_path, delimiter=" ")
        else:
            VAMPIRE_input = pd.read_table(file_path + "input.txt", delimiter=" ")
    else:
        raise Exception("File path is not a valid input.txt file")

