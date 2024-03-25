

def ExtractReservoirOutput(file_path:str):

    if ".txt" in file_path:
        pass
    else:
        file_path = file_path + "/reservoir_output.txt"

    with open(file_path, "r") as file:
        data = file.readlines()
        file.close()

    print((data))

ExtractReservoirOutput("/home/matteo/Desktop/VAMPIRE_WORKDIR/reservoir_output.txt")
