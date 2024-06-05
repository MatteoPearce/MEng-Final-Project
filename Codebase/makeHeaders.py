
"""
MAKE THE FIRST TWO LINES OF THE sourcefield.txt FILE ACCORDING TO GRID SIZE AND NUMBER OF CELLS

the format of the header lines is always:

    x x x y y y z z z -2
    x y z x y z x y z -1

cell numbers cannot be 0.
"""
def make_headers(cells_perX: int, cells_perY: int) -> list:

    header1 = str()
    header2 = str()

    if cells_perX > cells_perY:
        bigger_dim = cells_perX
        smaller_dim = cells_perY
    else:
        bigger_dim = cells_perY
        smaller_dim = cells_perX

    for i in range(1, smaller_dim + 1):
        for j in range(1, bigger_dim + 1):
            header1 = header1 + f"{i} "

    for i in range(1, bigger_dim+1):
        header2 = header2 + f"{i} "

    dummy = header2
    for i in range(smaller_dim - 1):
        header2 = header2 + dummy

    headers = [header1, header2]

    return headers
