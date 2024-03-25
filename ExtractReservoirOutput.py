import numpy as np

def ExtractReservoirOutput(file_path:str):

    if ".txt" in file_path:
        pass
    else:
        file_path = file_path + "/reservoir_output.txt"

    with open(file_path, "r") as file:
        numpy_array = np.empty((1,len(file.readline().split(" "))-1),dtype=float)
        data = file.readlines()
        file.close()

    for line in data:
        dummy_list = line.split(" ")
        dummy_list.pop(-1)
        dummy_array = np.asarray(dummy_list,dtype=float)
        dummy_array = dummy_array.reshape((1,len(dummy_list)))
        numpy_array = np.concatenate((numpy_array,dummy_array),axis=0)

    #print(numpy_array.shape)
    return numpy_array

ExtractReservoirOutput("/home/matteo/Desktop/VAMPIRE_WORKDIR/reservoir_output.txt")
