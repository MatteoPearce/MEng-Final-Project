import shutil
import os
import matplotlib.pyplot as plt
import numpy as np

"""
CREATES A FOLDER IN THE TEST DATA PATH LABELED WITH THE ITERATION NUMBER. SAVES A TEXT FILE CALLED accuracy_scores.txt 
CONTAINING ALL OF THE COMBINATION PARAMETERS FOR THE CURRENT TEST, CREATES A PLOT OF THE PREDICTION TRACE OVERLAID ON
THE INPUT TRACE AND COPIES THE VAMPIRE SPECIFIC FILES TO THE DIRECTORY, SO THAT RESULTS ARE REPRODUCIBLE.
"""

def save_data(data: dict = None, dir_name: str = None, save_path: str = None, workdir_path: str = None, Failed : bool = False) -> None:

    if dir_name is not None and save_path is not None and workdir_path is not None:

        # identify material file
        for file in os.listdir(workdir_path):
            filename = os.fsdecode(file)
            if filename.endswith(".mat"):
                mat_file = file
                break

        # files for reproducibility
        files_to_copy = list()
        files_to_copy.append(workdir_path + '/input')
        files_to_copy.append(workdir_path + '/reservoir_output.txt')
        files_to_copy.append(workdir_path + f'/{mat_file}')

        destination_directory = save_path + dir_name

        # creates directory named after iteration number
        if os.path.exists(destination_directory):
            shutil.rmtree(destination_directory)
        os.mkdir(destination_directory)

        # copies vampire files over to new directory
        for file in files_to_copy:
            try:
                shutil.copy(file, destination_directory)
            except:
                pass

        if data is not None:

            if not Failed: # cannot plot prediction if training step failed.

                plt.plot(np.arange(data['y_pred'].shape[0]), data['y'][:, 0], marker='o', markersize=1)  # , color='red')
                plt.plot(np.arange(data['y_pred'].shape[0]), data['y_pred'][:, 0], marker='o', markersize=1)
                plt.xlabel('Time')  # X-axis label
                plt.ylabel('Magnitude')  # Y-axis label
                plt.title('Prediction')  # title of the plot
                plt.savefig(destination_directory + '/prediction task')
                plt.close()

                data.pop('y')
                data.pop('y_pred')

            with open(destination_directory + '/accuracy_scores.txt',"w") as file:
                for key, value in data.items():
                    file.writelines(key + ": " + str(value) + "\n")
                file.close()



