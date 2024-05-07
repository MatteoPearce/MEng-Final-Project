
def makeHeaders(cells_perX: int, cells_perY: int) -> list:

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

#makeHeaders(5,10)