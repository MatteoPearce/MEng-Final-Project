import shutil
import os
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
            shutil.copy2(file, destination_directory)

#----------------------------------------------------------------------------------------------------------------------#

saveData(data=None,
         dir_name="/test",
         save_path="/home/matteo/Desktop/VAMPIRE_TEST_RESULTS",
         workdir_path="/home/matteo/Desktop/VAMPIRE_WORKDIR")


