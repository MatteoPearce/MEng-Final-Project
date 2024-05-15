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

def train_ridge(workdir_path: str = None, target: np.ndarray = None) -> tuple[float,float,np.ndarray,np.ndarray]:

    if workdir_path is not None:

        training_split = np.arange(0.5,0.95,0.05)

        if not os.path.isfile(os.path.join(workdir_path,"reservoir_output.txt")):
            return None, None, None, None
        else:
            throwaway, output_array = ERO(workdir_path + "/sourcefield.txt",
                                            workdir_path + "/reservoir_output.txt") # get input and output files

            # MIN-MAX normalisation step. RR works poorly on really small values
            target = (target - target.min()) / (target.max() - target.min())
            #target = np.tile(target, (1, output_array.shape[1]))  # repeat timeseries for every cell
            output_array = (output_array - output_array.min()) / (output_array.max() - output_array.min())

            best_result = np.inf
            best_split = 0

            for split in tqdm(training_split):

                lower_limit = int(split * target.shape[0])
                upper_limit = target.shape[0]

                training_y = target[:lower_limit]
                training_X = output_array[:lower_limit, :]
                testing_y = target[lower_limit:]
                testing_X = output_array[lower_limit:upper_limit, :]

                try:
                    NMSE, training_NMSE, y, y_pred = train_cycle( training_X, training_y, testing_X, testing_y)
                except np.linalg.LinAlgError:
                    NMSE, training_NMSE, y, y_pred = None, None, None, None
                    break

                if NMSE is not None:
                    if NMSE < best_result:
                        best_result = NMSE
                        best_training = training_NMSE
                        best_y = y
                        best_y_pred = y_pred
                        best_split = split

            if NMSE is not None:

                print(f"\nbest split: {best_split}")

                best_y = best_y - 0.5 # centre around 0
                best_y_pred = best_y_pred - 0.5

                return best_result, best_training, best_y, best_y_pred

            else:
                return None, None, None, None

#----------------------------------------------------------------------------------------------------------------------#
def train_cycle(training_X: np.ndarray,
                training_y: np.ndarray,
                testing_X: np.ndarray,
                testing_y: np.ndarray) -> [float,float,np.ndarray,np.ndarray]:

    ridges = [10e0,10e-1,10e-2,10e-3,10e-4,10e-5,10e-6,10e-7,10e-8,10e-9,10e-10,10e-11,10e-12,10e-13,10e-14,10e-15]

    best = np.inf
    best_training = None
    best_y = None
    best_pred = None

    for ridge in ridges:

        output_node = Ridge(output_dim=testing_y.shape[1],ridge=ridge)
        try: # sometimes vampire outputs are NAN. using try statement mitigates crashes and deems this combination a failure
            fitted_output = output_node.fit(training_X, training_y, warmup=200)
            prediction = fitted_output.run(testing_X)
            training_rerun = fitted_output.run(training_X)
            clip_size = 2 # last two datapoints are often massive offshoots
            new_limit = testing_y.shape[0] - clip_size
            clipped_prediction = prediction[:new_limit, :]
            clipped_testing_y = testing_y[:new_limit, :]

            clipped_rerun = training_rerun[:new_limit, :]
            clipped_training_y = training_y[:new_limit, :]

            NMSE = robs.nrmse(testing_y.copy(), prediction.copy(),norm="var")
            training_NMSE = robs.nrmse(training_y.copy(),training_rerun.copy(),norm="var")

            del output_node
            del fitted_output

            if NMSE < best:
                best = NMSE
                best_training = training_NMSE
                best_pred = prediction
                best_y = testing_y

        except ValueError:
            return None, None, None, None

    return best, best_training, best_y, best_pred

#----------------------------------------------------------------------------------------------------------------------#
