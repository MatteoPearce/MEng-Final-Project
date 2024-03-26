import numpy as np

def ExtractReservoirIO(file_path1: str,file_path2: str = None) -> np.ndarray:

    paths = [file_path1, file_path2]
    output_arrays = list()
    if file_path2 is None:
        paths.pop(1)

    for file_path in paths:

        with open(file_path, "r") as file:
            cell_num = len(file.readline().split(" "))-1
            data = file.readlines()
            file.close()

        for index, line in enumerate(data):

            dummy_list = line.strip().split(" ")

            if len(dummy_list) > cell_num:
                dummy_list.pop(-1)

            dummy_array = np.asarray(dummy_list,dtype=np.float128)
            dummy_array = dummy_array.reshape((1,len(dummy_list)))

            if index == 0:
                numpy_array = dummy_array
            else:
                numpy_array = np.concatenate((numpy_array,dummy_array),axis=0)

        output_arrays.append(numpy_array)

    return output_arrays

#ExtractReservoirOutput("/home/matteo/Desktop/VAMPIRE_WORKDIR/reservoir_output.txt")
