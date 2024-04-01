from random import randint
from typing import Tuple, Any

from Sourcefield_Filemaker import filemaker
import numpy as np
from GenerateTimeseries import GenerateTimeseries as GT
def scaleGrid(x_dims: list = None,
              y_dims: list = None,
              cell_dim: list = None,
              save_path: str = None,
              timeseries: np.ndarray = None) -> tuple[int | Any, int | Any, Any]:

    valid_choice = False
    counter = 0
    while not valid_choice:
        dim_choiceX = x_dims[randint(0, len(x_dims)-1)] + 1
        dim_choiceY = y_dims[randint(0, len(y_dims)-1)] + 1
        dim_choiceCELL = cell_dim[randint(0, len(cell_dim)-1)]

        cells_perX = dim_choiceX / dim_choiceCELL
        cells_perY = dim_choiceY / dim_choiceCELL

        if cells_perX % 1 == 0 and cells_perY % 1 == 0:
            valid_choice = True

        if counter >= 10000:
            break

        counter += 1

    if valid_choice:

        return dim_choiceX -1, dim_choiceY -1, dim_choiceCELL

    else:

        print("COULD NOT FIND ANY DIMENSIONS")
        return 49, 49, 5
