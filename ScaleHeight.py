import os
def scaleHeight(file_path: str = None, height: float = None) ->float:

    success = False
    for file in os.listdir(file_path):
        filename = os.fsdecode(file)
        if filename.endswith(".mat"):
            mat_file = file
            success = True
            with open(os.path.join(file_path, file), "r") as f:
                data = f.readlines()
                f.close()

    if success:
        for line in data:
            if "unit cell size" in line:
                unit_cell_size = float(line.split(" = ")[1].replace(" !A",""))
                print(unit_cell_size)
                break

        if (height < 1) or (height % unit_cell_size == 0):
            return height
        else:
            scaled_height = int (height / unit_cell_size) * unit_cell_size
            return scaled_height