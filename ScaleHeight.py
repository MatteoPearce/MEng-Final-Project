import os

"""
RECEIVES THE MATERIAL UNDER TEST, THE PATH WHERE ITS .mat FILE IS SAVED AND THE REQUESTED HEIGHT. THE UNIT CELL SIZE 
IS EXTRACTED FROM THE .mat FILE AND ITS MULTIPLE NEAREST TO THE REQUESTED HEIGHT IS RETURNED. 
"""

def scale_height(file_path: str = None, material: str = None, height: float = None) ->float:

    # extract material file
    success = False
    for file in os.listdir(file_path):
        filename = os.fsdecode(file)
        if filename == material:
            success = True
            with open(os.path.join(file_path, file), "r") as f:
                data = f.readlines()
                f.close()
            break

    if success:
        for line in data:
            # unit cell size in the 2nd commented line in .mat file
            if "unit cell size" in line:
                unit_cell_size = float(line.split(" = ")[1].replace(" !A",""))
                break

        # if height is less than 1A then vampire will create a monolayer. if height already multiple, do nothing.
        if (height < 1) or (height % unit_cell_size == 0):
            return height
        else:
            scaled_height = int(height / unit_cell_size) * unit_cell_size # return multiple.
            scaled_height = round(scaled_height, 4)
            return scaled_height