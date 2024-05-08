from typing import Tuple, Any
import matplotlib.pyplot as plt
import reservoirpy
from reservoirpy.nodes import Ridge
from reservoirpy import observables as robs
import numpy as np
from tqdm import tqdm
from ExtractReservoirIO import extract_reservoir_IO as ERO
import os
reservoirpy.verbosity(0)

"""
INSTANTIATE RIDGE LAYER OF NEURONS EQUAL TO NUMBER OF CELLS. TRIAL DIFFERENT TRAINING SPLITS AND THEN PERFORM A 
LEAVE-ONE-OUT CROSS VALIDATION. THE ASSESSMENT IS A PREDICTION TASK AND THE OPTIMISATION FUNCTION IS A RIDGE REGRESSION 

The ridge instantiation, data fitting and calculating the NMSE are performed with wrapper functions from the
reservoirpy package (https://reservoirpy.readthedocs.io/en/latest/#).

The highest NMSE achieved on unseen data is preserved and compared to each new data split. after the optimal data split 
is found, a leave-one-out cross validation is performed to see if the NMSE can further be improved.

The best NMSE, the NMSE achieved on the training data and the traces of the prediction and original trace are returned. 
Both training functions call the train_cyle method for the actual training step and returns None for all if anything 
fails. 

The respective links to each calculation can be found here:

ridge:                  https://reservoirpy.readthedocs.io/en/latest/api/generated/reservoirpy.nodes.Ridge.html
ridge regression:       https://reservoirpy.readthedocs.io/en/latest/api/generated/reservoirpy.compat.regression_models.RidgeRegression.html
NMSE:                   https://reservoirpy.readthedocs.io/en/latest/api/generated/reservoirpy.observables.nrmse.html#reservoirpy.observables.nrmse

all arrays are of shape (timesteps, cells). The output arrays are always longer because vampire simulates beyond the 
requested simulation steps and therefore it needs to be clipped in dimension 0 to match the length of the input array.
"""

def train_ridge(workdir_path: str = None) -> tuple[float,float,np.ndarray,np.ndarray]:

    if workdir_path is not None:

        training_split = np.arange(0.5,0.95,0.05)

        if not os.path.isfile(os.path.join(workdir_path,"reservoir_output.txt")):
            return None, None, None, None
        else:
            input_array, output_array = ERO(workdir_path + "/sourcefield.txt",
                                            workdir_path + "/reservoir_output.txt") # get input and output files

            input_array = np.delete(input_array, 0, axis=0)
            best_result = np.inf
            best_split = 0

            for split in tqdm(training_split):

                lower_limit = int(split * input_array.shape[0])
                upper_limit = input_array.shape[0]

                training_y = input_array[:lower_limit, :]
                training_X = output_array[:lower_limit, :]
                testing_y = input_array[lower_limit:, :]
                testing_X = output_array[lower_limit:upper_limit, :]

                try:
                    NMSE, training_NMSE, y, y_pred = train_cycle( training_X, training_y, testing_X, testing_y)
                except np.linalg.LinAlgError:
                    NMSE, training_NMSE, y, y_pred = None, None, None, None
                    break

                if NMSE is not None:
                    if NMSE < best_result:
                        best_result = NMSE
                        best_split = split

            if NMSE is not None:

                print(f"\nbest split: {best_split}")

                best_result, best_training, y, y_pred = loo_crossval(input_array, output_array, best_split)

                return best_result, best_training, y, y_pred

            else:
                return None, None, None, None

#----------------------------------------------------------------------------------------------------------------------#
def loo_crossval(input_array: np.ndarray,
                 output_array: np.ndarray,
                 split: float = None) -> [float,float,np.ndarray,np.ndarray]:

    if split is not None:

        best_result = np.inf
        best_training = np.inf
        updated = False

        intervals = int(round(1 / (1- split),1))

        for i in tqdm(range(intervals)):

            step = int(input_array.shape[0] / intervals)

            testing_y = input_array[i * step:(i+1) * step,:]
            testing_X = output_array[i * step:(i+1) * step,:]
            rows = np.arange(i * step,(i+1) * step)
            training_y = np.delete(input_array,rows,axis=0)
            training_X = output_array[:input_array.shape[0], :]
            training_X = np.delete(training_X,rows,axis=0)

            try:
                NMSE, training_NMSE, y, y_pred = train_cycle(training_X, training_y, testing_X, testing_y)
            except np.linalg.LinAlgError:
                return None, None, None, None


            if NMSE is not None:
                if NMSE < best_result:
                    updated = True
                    best_result = NMSE
                    best_training = training_NMSE
                    best_y = y
                    best_y_pred = y_pred

        if updated:
            return best_result, best_training, best_y, best_y_pred

        else:
            return None, None, None, None

#----------------------------------------------------------------------------------------------------------------------#
def train_cycle(training_X: np.ndarray,
                training_y: np.ndarray,
                testing_X: np.ndarray,
                testing_y: np.ndarray) -> [float,float,np.ndarray,np.ndarray]:

    output_node = Ridge(output_dim=testing_y.shape[1],ridge=1e-50)
    try: # sometimes vampire outputs are NAN. using try statement mitigates crashes and deems this combination a failure
        fitted_output = output_node.fit(training_X, training_y, warmup=10)
        prediction = fitted_output.run(testing_X)
        training_rerun = fitted_output.run(training_X)

        clip_size = 2 # last two datapoints are often massive offshoots
        new_limit = testing_y.shape[0] - clip_size
        clipped_prediction = prediction[:new_limit, :]
        clipped_testing_y = testing_y[:new_limit, :]

        clipped_rerun = training_rerun[:new_limit, :]
        clipped_training_y = training_y[:new_limit, :]

        NMSE = robs.nrmse(clipped_testing_y, clipped_prediction)
        training_NMSE = robs.nrmse(clipped_training_y,clipped_rerun)

        del output_node
        del fitted_output

        return NMSE, training_NMSE, clipped_testing_y, clipped_prediction
    except ValueError:
        return None, None, None, None

#----------------------------------------------------------------------------------------------------------------------#
