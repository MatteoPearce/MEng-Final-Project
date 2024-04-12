import os
def recoupData(test_data_path: str, threshold: float = None, training: bool = False):

    all_data = str()

    for dir in os.listdir(test_data_path):
        dirname = os.fsdecode(dir)

        if "FAILED" in dirname:
            pass
        else:
            for file in os.listdir(os.path.join(test_data_path, dir)):
                filename = os.fsdecode(file)
                if filename == "accuracy_scores.txt":
                    #print(filename)
                    with open(os.path.join(test_data_path, dir, file), "r") as f:
                        new_data = f.readlines()
                        f.close()

                    if threshold is not None:

                        for line in new_data:
                            if training:
                                if "training_NRMSE" in line:
                                    nrmse = float(line.split(": ")[1])
                                    break
                            else:
                                if "NRMSE" in line :
                                    if "training_NRMSE" in line:
                                        pass
                                    else:
                                        nrmse = float(line.split(": ")[1])
                                        break

                        if nrmse < threshold:

                            for line in new_data:
                                all_data += str(line).replace(": ", " = ")
                            all_data += "iteration = " + dirname + "\n"
                            all_data += "\n"
                            break

                    else:

                        for line in new_data:
                            all_data += str(line).replace(": ", " = ")
                        all_data += "iteration = " + dirname + "\n"
                        all_data += "\n"
                        break



    with open(os.path.join(test_data_path, "best_iteration.txt"), "w") as f:
        f.write(all_data)
        f.close()

#----------------------------------------------------------------------------------------------------------------------#

recoupData( "/home/matteo/Desktop/VAMPIRE_TEST_RESULTS",training=True )
