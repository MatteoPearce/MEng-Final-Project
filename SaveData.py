import shutil
import os
import matplotlib.pyplot as plt
import numpy as np
def saveData(data: dict = None, dir_name: str = None, save_path: str = None, workdir_path: str = None) -> None:

    if dir_name is not None and save_path is not None and workdir_path is not None:

        for file in os.listdir(workdir_path):
            filename = os.fsdecode(file)
            if filename.endswith(".mat"):
                mat_file = file
                break

        files_to_copy = list()
        files_to_copy.append(workdir_path + '/input')
        files_to_copy.append(workdir_path + '/output')
        files_to_copy.append(workdir_path + '/reservoir_output.txt')
        files_to_copy.append(workdir_path + f'/{mat_file}')

        destination_directory = save_path + dir_name
        os.mkdir(destination_directory)

        # shutil.copy2() preserves original metadata
        for file in files_to_copy:
            shutil.copy(file, destination_directory)

        if data is not None:

            plt.plot(np.arange(data['y_pred'].shape[0]), data['y'][:, 0], marker='o', markersize=1)  # , color='red')
            plt.plot(np.arange(data['y_pred'].shape[0]), data['y_pred'][:, 0], marker='o', markersize=1)
            plt.xlabel('Time')  # X-axis label
            plt.ylabel('Magnitude')  # Y-axis label
            plt.title('Prediction');  # title of the plot
            plt.savefig(destination_directory + '/prediction task')

            data.pop('y')
            data.pop('y_pred')

            with open(destination_directory + '/accuracy_scores.txt',"w") as file:
                for key, value in data.items():
                    file.writelines(key + ": " + str(value) + "\n")
                file.close()

#----------------------------------------------------------------------------------------------------------------------#

"""
y = np.arange(0,10)
y_pred = np.arange(0,10)
y = y.reshape((1,10))
y_pred = y_pred.reshape((1,10))

data = {"y_pred": y_pred,
        "y": y,
        "NRMSE" : 0.14,
        "MSE" : 0.2}

saveData(data=data,
         dir_name="/test",
         save_path="/home/matteo/Desktop/VAMPIRE_TEST_RESULTS",
         workdir_path="/home/matteo/Desktop/VAMPIRE_WORKDIR")
"""


