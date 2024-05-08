from random import randint
from typing import Tuple, Any

"""
RECEIVES THE LISTS OF FILM X,Y,CELL DIMENSIONS TO EXPLORE AND WORKS OUT RANDOM CONFIGURATION WHERE X,Y ARE MULTIPLES
OF CELL DIM. IF NO COMBINATIONS ARE VALID IF RETURNS "DEFAULT" GRID OF 50nm x 50nm WITH 5nm CELL.
"""

def scale_grid(x_dims: list = None,
              y_dims: list = None,
              cell_dim: list = None) -> tuple[int | Any, int | Any, Any]:

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
        # for simplicity, x dim is always chosen as the bigger dim, to avoid the same combinations being tested twice
        if dim_choiceX < dim_choiceY:

            dummy = dim_choiceX
            dim_choiceX = dim_choiceY
            dim_choiceY = dummy

        return dim_choiceX -1, dim_choiceY -1, dim_choiceCELL

    else:
        print("COULD NOT FIND ANY DIMENSIONS")
        return 49, 49, 5
