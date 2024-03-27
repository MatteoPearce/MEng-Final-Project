import reservoirpy
from reservoirpy.nodes import Ridge
from reservoirpy import observables as robs
import numpy as np
from tqdm import tqdm
from ExtractReservoirIO import ExtractReservoirIO as ERO
import matplotlib.pyplot as plt
np.set_printoptions(threshold=np.inf)
reservoirpy.verbosity(0)

def TrainGS(workdir_path: str = None) -> float:

    if workdir_path is not None:

        training_split = np.arange(0.5,0.95,0.05)

        input_array, output_array = ERO(workdir_path + "/sourcefield.txt",
                                        workdir_path + "/reservoir_output.txt")

        input_array = np.delete(input_array, 0, axis=0)
        neuron_number = input_array.shape[1]
        print("Performing Grid Search of best training split \n")

        for split in tqdm(training_split):

            best_result = 1
            best_split = 0

            scaling_factor = 1
            lower_limit = int(split * input_array.shape[0])
            upper_limit = input_array.shape[0]

            training_y = input_array[:lower_limit, :]
            training_X = output_array[:lower_limit, :] * scaling_factor
            testing_y = input_array[lower_limit:, :]
            testing_X = output_array[lower_limit:upper_limit, :] * scaling_factor

            NRMSE = train_cycle( training_X, training_y, testing_X, testing_y)

            if NRMSE < best_result:
                best_result = NRMSE
                best_split = split

        print(f"best split: {best_split}")
        best_result = trainCV(input_array, output_array, neuron_number, best_split)

        return best_result

def trainCV(input_array: np.ndarray, output_array: np.ndarray, neuron_number: int, split: float = None) -> float:

    if split is not None:

        if split <= 0.1:
            split = 0.9

        intervals = int(round(1 / (1- split),1))

        for i in tqdm(range(intervals)):

            step = int(input_array.shape[0] / intervals)

            testing_y = input_array[i * step:(i+1) * step,:]
            testing_X = output_array[i * step:(i+1) * step,:]
            rows = np.arange(i * step,(i+1) * step)
            training_y = np.delete(input_array,rows,axis=0)
            training_X = output_array[:input_array.shape[0], :]
            training_X = np.delete(training_X,rows,axis=0)

            NRMSE = train_cycle( training_X, training_y, testing_X, testing_y)

        return NRMSE

#----------------------------------------------------------------------------------------------------------------------#
def train_cycle(training_X: np.ndarray,
                training_y: np.ndarray,
                testing_X: np.ndarray,
                testing_y: np.ndarray) -> float:

    output_node = Ridge(output_dim=testing_y.shape[1])  # , name="output_node ")
    fitted_output = output_node.fit(training_X, training_y, warmup=0)
    prediction = fitted_output.run(testing_X)

    clip_size = 2
    new_limit = testing_y.shape[0] - clip_size
    clipped_prediction = prediction[:new_limit, :]
    clipped_testing_y = testing_y[:new_limit, :]

    NRMSE = robs.nrmse(clipped_testing_y, clipped_prediction)

    plt.plot(np.arange(clipped_prediction.shape[0]), clipped_testing_y[:, 0], marker='o', markersize=1)  # , color='red')
    plt.plot(np.arange(clipped_prediction.shape[0]), clipped_prediction[:,0], marker='o', markersize=1)
    plt.xlabel('Time')  # X-axis label
    plt.ylabel('Magnitude')  # Y-axis label
    plt.title('Prediction');  # title of the plot
    plt.show()

    del output_node
    del fitted_output

    return NRMSE

#----------------------------------------------------------------------------------------------------------------------#

best_result = TrainGS("/home/matteo/Desktop/VAMPIRE_WORKDIR")
print(f"best_result = {best_result}")
