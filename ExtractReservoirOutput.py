

def ExtractReservoirOutput(file_path:str):

    if ".txt" in file_path:
        pass
    else:
        file_path = file_path + "/reservoir_output.txt"

    with open(file_path, "r"):
        data = readlines()
