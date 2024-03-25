import numpy as np

def ExtractReservoirOutput(file_path:str):

    if ".txt" in file_path:
        pass
    else:
        file_path = file_path + "/reservoir_output.txt"

    with open(file_path, "r") as file:
        numpy_array = np.empty((1,len(file.readline())),dtype=float)
        data = file.readlines()
        file.close()

    for line in data:

        dummy_array = np.asarray(line.join(""))
        #print(type(dummy_array))
        print(dummy_array)
        input()
        dummy_array = dummy_array.reshape((1,len(line)))
        numpy_array = np.concatenate((numpy_array,dummy_array),axis=0)

    print(numpy_array)

ExtractReservoirOutput("/home/matteo/Desktop/VAMPIRE_WORKDIR/reservoir_output.txt")
