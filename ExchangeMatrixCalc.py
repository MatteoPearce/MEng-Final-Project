
def exchangeMatrixCalc(crystal,const,stiffie):

    nearestNeighbours = {"fcc" : 12,
                         "bcc" : 8,
                         "sc": 6,
                         "hcp": 12}

    lattice_consts = {"Fe_bcc": 2.886e-9,
                      "Fe_fcc": 3.571e-9,
                      "Ni": 3.524e-9,
                      "Co": 2.507e-9}

    Spinwave_stiffies = {"Fe": 21e-12,
                         "Ni": 15e-12,
                         "Co": 56e-12}

    J_ij = Spinwave_stiffies[stiffie] * lattice_consts[const] / nearestNeighbours[crystal]
    print(J_ij)

exchangeMatrixCalc("fcc","Ni","Ni")