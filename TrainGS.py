import reservoirpy
from reservoirpy.nodes import Ridge
from reservoirpy import observables as robs
import numpy as np
from tqdm import tqdm
from ExtractReservoirIO import ExtractReservoirIO as ERO
np.set_printoptions(threshold=np.inf)
reservoirpy.verbosity(0)

def TrainGS(workdir_path: str = None):

    if workdir_path is not None:

        training_split = np.arange(0.5,0.95,0.05)

        input_array, output_array = ERO(workdir_path + "/sourcefield.txt",
                                        workdir_path + "/reservoir_output.txt")

        input_array = np.delete(input_array, 0, axis=0)
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

            output_node = Ridge(output_dim=input_array.shape[1])#, name="output_node ")
            fitted_output = output_node.fit(training_X, training_y, warmup=0)
            prediction = fitted_output.run(testing_X)

            clip_size = 2
            new_limit = upper_limit - lower_limit - clip_size
            clipped_prediction = prediction[:new_limit, :]
            clipped_testing_y = testing_y[:new_limit, :]

            #MSE = robs.mse(clipped_testing_y, clipped_prediction)
            #RMSE = robs.rmse(clipped_testing_y, clipped_prediction)
            NRMSE = robs.nrmse(clipped_testing_y, clipped_prediction)
            #R_2 = robs.rsquare(clipped_testing_y, clipped_prediction)

            if NRMSE < best_result:
                best_result = NRMSE
                best_split = split

            del output_node
            del fitted_output

        return best_result, best_split

best_result, best_split = TrainGS("/home/matteo/Desktop/VAMPIRE_WORKDIR")

print(best_result)
print(best_split)
