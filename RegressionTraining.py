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

The ridge instantiation, data fitting and calculating the NRMSE are performed with wrapper functions from the
reservoirpy package (https://reservoirpy.readthedocs.io/en/latest/#).

The highest NRMSE achieved on unseen data is preserved and compared to each new data split. after the optimal data split 
is found, a leave-one-out cross validation is performed to see if the NRMSE can further be improved.

The best NRMSE, the NRMSE achieved on the training data and the traces of the prediction and original trace are returned. 
Both training functions call the train_cyle method for the actual training step and returns None for all if anything 
fails. 

The respective links to each calculation can be found here:

ridge:                  https://reservoirpy.readthedocs.io/en/latest/api/generated/reservoirpy.nodes.Ridge.html
ridge regression:       https://reservoirpy.readthedocs.io/en/latest/api/generated/reservoirpy.compat.regression_models.RidgeRegression.html
NRMSE:                   https://reservoirpy.readthedocs.io/en/latest/api/generated/reservoirpy.observables.nrmse.html#reservoirpy.observables.nrmse

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

            log_target = np.log1p(target)  # Logarithmic transformation with added 1 to handle zeros
            log_training = np.log1p(output_array)

            standardized_target = (log_target - np.mean(log_target)) / np.std(log_target)
            standardized_training = (log_training - np.mean(log_training)) / np.std(log_training)

            best_result = np.inf
            best_split = 0

            for split in tqdm(training_split):

                lower_limit = int(split * target.shape[0])
                upper_limit = target.shape[0]

                training_y = standardized_target[:lower_limit]
                training_X = standardized_training[1:lower_limit, :] # shift by 1 to ensure causality
                training_X = np.insert(training_X, 0,0, axis=0)
                testing_y = standardized_target[lower_limit:]
                testing_X = standardized_training[lower_limit:upper_limit, :]

                try:
                    NRMSE, training_NRMSE, y, y_pred = train_cycle( training_X, training_y, testing_X, testing_y)
                except np.linalg.LinAlgError:
                    NRMSE, training_NRMSE, y, y_pred = None, None, None, None
                    break

                if NRMSE is not None:
                    if NRMSE < best_result:
                        best_result = NRMSE
                        best_training = training_NRMSE
                        best_y = y
                        best_y_pred = y_pred
                        best_split = split

            if NRMSE is not None:

                print(f"\nbest split: {best_split}")

                return best_result, best_training, best_y, best_y_pred

            else:
                return None, None, None, None

#----------------------------------------------------------------------------------------------------------------------#
def train_cycle(training_X: np.ndarray,
                training_y: np.ndarray,
                testing_X: np.ndarray,
                testing_y: np.ndarray) -> [float,float,np.ndarray,np.ndarray]:

    ridges = [0]#[10e-2,10e-3,10e-4,0]

    best = np.inf
    best_training = None
    best_y = None
    best_pred = None

    for ridge in ridges:

        output_node = Ridge(output_dim=testing_y.shape[1],ridge=ridge)
        try: # sometimes vampire outputs are NAN. using try statement mitigates crashes and deems this combination a failure
            fitted_output = output_node.fit(training_X, training_y, warmup=int(training_y.shape[0]/5))
            prediction = fitted_output.run(testing_X)
            training_rerun = fitted_output.run(training_X)

            NRMSE = robs.nrmse(testing_y.copy(), prediction.copy(),norm="var")
            training_NRMSE = robs.nrmse(training_y.copy(),training_rerun.copy(),norm="var")

            del output_node
            del fitted_output

            if NRMSE < best:
                best = NRMSE
                best_training = training_NRMSE
                best_pred = prediction
                best_y = testing_y
                best_ridge = ridge


        except ValueError as e:
            print(e)
            return None, None, None, None

    #print(f"\nbest ridge: {best_ridge}")

    return best, best_training, best_y, best_pred

#----------------------------------------------------------------------------------------------------------------------#
