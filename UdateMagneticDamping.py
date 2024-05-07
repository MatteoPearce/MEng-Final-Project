import os

def updateDamping(dir_path: str, magneticDamping: float):

    success = False
    for file in os.listdir(dir_path):
        filename = os.fsdecode(file)
        if filename.endswith(".mat"):
            mat_file = file
            success = True
            with open(os.path.join(dir_path, file), "r") as f:
                data = f.readlines()
                f.close()

    if success:
        for index,line in enumerate(data):
            if "material[1]:damping-constant=" in line:
                old_damping = line.split("=")[1]
                data[index] = line.replace(old_damping,str(magneticDamping)+"\n")

        with open(os.path.join(dir_path, mat_file), "w") as f:
            f.writelines(data)
            f.close()

    else:
        print("COULDN'T FIND MATERIAL FILE")

#updateDamping("/home/matteo/Desktop/VAMPIRE_WORKDIR",0.12345)