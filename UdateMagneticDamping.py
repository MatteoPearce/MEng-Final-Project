import os

"""
CHANGES THE VALUE FOR GILBERT INTRINSIC MAGNETIC DAMPING IN THE .mat MATERIAL FILE. 

Magnetic damping is the only material file parameter that is changed in any of the explorations. The number is selected
in main and passed to update_damping, which opens the .mat file in the working directory and changes the value. 
"""

def update_damping(dir_path: str, magneticDamping: float):

    if os.path.exists(dir_path):
        success = False
        # open material file
        for file in os.listdir(dir_path):
            filename = os.fsdecode(file)
            if filename.endswith(".mat"):
                mat_file = file
                success = True
                # read data
                with open(os.path.join(dir_path, file), "r") as f:
                    data = f.readlines()
                    f.close()

        if success:
            # find damping and modify data
            for index,line in enumerate(data):
                if "material[1]:damping-constant=" in line:
                    old_damping = line.split("=")[1]
                    data[index] = line.replace(old_damping,str(magneticDamping)+"\n")

            # rewrite data to material file
            with open(os.path.join(dir_path, mat_file), "w") as f:
                f.writelines(data)
                f.close()

        else:
            print("COULDN'T FIND MATERIAL FILE")

    else:
        print("NO MATERIAL FILE FOUND")