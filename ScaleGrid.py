from random import randint
from Sourcefield_Filemaker import filemaker
import numpy as np
from GenerateTimeseries import GenerateTimeseries as GT
def scaleGrid(x_dims: list = None,
              y_dims: list = None,
              cell_dim: list = None,
              save_path: str = None,
              timeseries: np.ndarray = None) -> None:

    valid_choice = False
    while not valid_choice:
        dim_choiceX = x_dims[randint(0, len(x_dims)-1)] + 1
        dim_choiceY = y_dims[randint(0, len(y_dims)-1)] + 1
        dim_choiceCELL = cell_dim[randint(0, len(cell_dim)-1)]

        cells_perX = dim_choiceX / dim_choiceCELL
        cells_perY = dim_choiceY / dim_choiceCELL

        if cells_perX % 1 == 0 and cells_perY % 1 == 0:
            valid_choice = True
            cells_perX = int(cells_perX)
            cells_perY = int(cells_perY)

    num_cells = int(cells_perX * cells_perY)

    print("dim_choiceX", dim_choiceX)
    print("dim_choiceY", dim_choiceY)
    print("dim_choiceCELL", dim_choiceCELL)
    print("num_cells", num_cells)

    header1 = str()
    header2 = str()

    if cells_perX > cells_perY:
        bigger_dim = cells_perX
        smaller_dim = cells_perY
    else:
        bigger_dim = cells_perY
        smaller_dim = cells_perX

    for i in range(1, cells_perX + 1):
        header1 = header1 + f"{i} "
        for j in range(1, cells_perY + 1):
            header2 = header2 + f"{i} "

    dummy = header1
    for i in range(cells_perY - 1):
        header1 = header1 + dummy

    print("header1", header1)
    print("header2", header2)
    #a = GT(stop_time=1000)
    filemaker(output_path=save_path,rows= a.shape[0],timeseries=a, columns=num_cells,all_same=True,headers=[header1,header2])

    return dim_choiceX -1, dim_choiceY -1, dim_choiceCELL


#a=[49,99,149,199]
#b=[49,99,149,199]
#c=[5,10,15,20]

#scaleGrid(a,b,c,save_path="/home/matteo/Desktop/VAMPIRE_WORKDIR")