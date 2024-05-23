import numpy as np
from tqdm import tqdm
from ExtractReservoirIO import extract_reservoir_IO as ERO
import os

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

all arrays are of shape (timesteps, cells). The output arrays are always longer because vampire simulates beyond the 
requested simulation steps and therefore it needs to be clipped in dimension 0 to match the length of the input array.
"""

def train_ridge(workdir_path: str = None, target: np.ndarray = None, signal_strength: float = None) -> tuple[any,any,any,any]:

    if workdir_path is not None:

        training_split = np.arange(0.5,0.95,0.05)

        if not os.path.isfile(os.path.join(workdir_path,"reservoir_output.txt")):
            return None, None, None, None
        else:
            throwaway, output_array = ERO(workdir_path + "/sourcefield.txt",
                                            workdir_path + "/reservoir_output.txt") # get input and output files

            output_array = (output_array / signal_strength)

            best_result = np.inf
            best_split = 0

            for split in tqdm(training_split):

                lower_limit = int(split * target.shape[0])
                upper_limit = target.shape[0]

                training_y = target[1:lower_limit]
                training_y = np.insert(training_y, 0, 0, axis=0)  # shift by 1 to ensure causality
                training_X = output_array[:lower_limit, :]
                testing_y = target[lower_limit:]
                testing_X = output_array[lower_limit:upper_limit, :]

                try:
                    NRMSE, training_NRMSE, y, y_pred = train_cycle( training_X, training_y, testing_X, testing_y,signal_strength)
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
                try:
                    return best_result, best_training, best_y, best_y_pred
                except:
                    return None, None, None, None

            else:
                return None, None, None, None

#----------------------------------------------------------------------------------------------------------------------#
def train_cycle(training_X: np.ndarray,
                training_y: np.ndarray,
                testing_X: np.ndarray,
                testing_y: np.ndarray,
                signal_strength: float) -> [float,float,np.ndarray,np.ndarray]:

    stop = signal_strength * training_X.shape[1]
    ridges = np.linspace(0,stop,10,endpoint=True)

    best = np.inf
    best_training = None
    best_y = None
    best_pred = None

    for RIDGE in ridges:

        try: # sometimes vampire outputs are NAN. using try statement mitigates crashes and deems this combination a failure

            term1 = np.dot(training_y.transpose(), training_X)
            term1_5 = np.dot(training_X.transpose(), training_X).astype(np.float64)
            identity_Size = term1_5.shape
            term2 = np.linalg.inv(term1_5 + np.dot(RIDGE,np.ones(identity_Size)))
            Wout = np.dot(term1,term2)

            prediction = np.dot(testing_X , Wout.transpose())
            training_rerun = np.dot(training_X, Wout.transpose())

            NRMSE = np.sqrt( (np.mean((prediction.copy() - testing_y.copy()) ** 2)) / np.var(testing_y))
            training_NRMSE = np.sqrt( (np.mean((training_rerun.copy() - training_y.copy()) ** 2)) / np.var(training_y))

            if NRMSE < best:
                best = NRMSE
                best_training = training_NRMSE
                best_pred = prediction.copy()
                best_y = testing_y.copy()
                best_ridge = RIDGE


        except ValueError as e:
            print(e)
            if best is not None:
                return best, best_training, best_y, best_pred
            else:
                return None, None, None, None

    print(f"\nbest ridge: {best_ridge}")

    return best, best_training, best_y, best_pred

#----------------------------------------------------------------------------------------------------------------------#
