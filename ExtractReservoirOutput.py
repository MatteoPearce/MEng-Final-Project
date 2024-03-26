import numpy as np

def ExtractReservoirIO(file_path1: str,file_path2: str = None) -> np.ndarray:

    paths = [file_path1, file_path2]
    output_arrays = list()
    if file_path2 is None:
        paths.pop(1)

    for file_path in paths:

        with open(file_path, "r") as file:
            numpy_array = np.empty((1,len(file.readline().split(" "))-1),dtype=float)
            data = file.readlines()
            file.close()

        for line in data:
            dummy_list = line.strip().split(" ")
            dummy_list.pop(-1)
            print(dummy_list)
            dummy_array = np.asarray(dummy_list,dtype=float)
            dummy_array = dummy_array.reshape((1,len(dummy_list)))
            numpy_array = np.concatenate((numpy_array,dummy_array),axis=0)

        output_arrays.append(numpy_array)

    #print(numpy_array.shape)
    return output_arrays

#ExtractReservoirOutput("/home/matteo/Desktop/VAMPIRE_WORKDIR/reservoir_output.txt")
