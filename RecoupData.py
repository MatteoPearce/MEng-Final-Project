import os

"""
EXTRACTS DATA FROM ALL ACCURACY SCORES FILES AND WRITES TO best_iterations.txt, WHICH IS USED BY CreatePlots.py TO
PLOT NMSE DATA.

threshold set manually to modify depth of data.
"""

def recoup_data(test_data_path: str, threshold: float = None, training: bool = False):

    all_data = str()

    for dir in os.listdir(test_data_path):
        dirname = os.fsdecode(dir)

        if "FAILED" in dirname: # skip failed runs
            pass
        else:
            for file in os.listdir(os.path.join(test_data_path, dir)):
                filename = os.fsdecode(file)
                if filename == "accuracy_scores.txt":

                    with open(os.path.join(test_data_path, dir, file), "r") as f:
                        new_data = f.readlines()
                        f.close()

                    if threshold is not None: # if threshold is specified, check

                        for line in new_data:
                            if training:
                                if "training_NMSE" in line:
                                    nmse = float(line.split(": ")[1])
                                    break
                            else:
                                if "NMSE" in line :
                                    if "training_NMSE" in line:
                                        pass
                                    else:
                                        nmse = float(line.split(": ")[1])
                                        break

                        if nmse < threshold:

                            for line in new_data:
                                all_data += str(line).replace(": ", " = ")
                            all_data += "iteration = " + dirname + "\n"
                            all_data += "\n"
                            break

                    else: # else grab all

                        for line in new_data:
                            all_data += str(line).replace(": ", " = ")
                        all_data += "iteration = " + dirname + "\n"
                        all_data += "\n"
                        break
    # create file
    with open(os.path.join(test_data_path, "best_iterations.txt"), "w") as f:
        f.write(all_data)
        f.close()

#----------------------------------------------------------------------------------------------------------------------#

dir = "/home/matteo/Desktop/VAMPIRE_TEST_RESULTS/"
recoup_data(dir , threshold=10)
