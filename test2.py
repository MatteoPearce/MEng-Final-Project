import reservoirpy as rpy
from reservoirpy.nodes import Ridge, Input
from reservoirpy import observables as robs
import numpy as np
from ExtractReservoirIO import ExtractReservoirIO as ERO
import matplotlib.pyplot as plt
from sklearn import preprocessing
np.set_printoptions(threshold=np.inf)

output_node = Ridge(output_dim = 100, name = "output_node ")

input_array, output_array = ERO("/home/matteo/Desktop/VAMPIRE_WORKDIR/sourcefield.txt",
                                "/home/matteo/Desktop/VAMPIRE_WORKDIR/reservoir_output.txt")
input_array = np.delete(input_array, 0, axis = 0)

scaling_factor = 1

lower_limit = int(0.75 * input_array.shape[0])
upper_limit = input_array.shape[0]

#print(np.average(output_array[:800,:] ))

training_y = input_array[:lower_limit,:]
training_X = output_array[:lower_limit,:] * scaling_factor
testing_y = input_array[lower_limit:,:]
testing_X = output_array[lower_limit:upper_limit,:] * scaling_factor

#print(np.average(training_X))

fitted_output = output_node.fit(training_X, training_y,warmup=0)

#print(f"ridge params: {fitted_output.params}")
#print(f"ridge hypers: {fitted_output.hypers}")

prediction = fitted_output.run(testing_X)

clip_size = 2
a = upper_limit - lower_limit - clip_size

clipped_prediction = prediction[:a,:]
clipped_testing_y = testing_y[:a,:]

#print(clipped_prediction.shape)
#print(clipped_testing_y.shape)

MSE = robs.mse(clipped_testing_y, clipped_prediction)
RMSE = robs.rmse(clipped_testing_y, clipped_prediction)
NRMSE = robs.nrmse(clipped_testing_y, clipped_prediction)
R_2 = robs.rsquare(clipped_testing_y, clipped_prediction)

print(f"MSE: {MSE}")
print(f"RMSE: {RMSE}")
print(f"NRMSE: {NRMSE}")
print(f"R_2: {R_2}")

#print(prediction[:,0])
for i in range(30):
    plt.plot(np.arange(clipped_prediction.shape[0]), clipped_testing_y[:,i], marker='o', markersize=1)#, color='red')
    plt.plot(np.arange(clipped_prediction.shape[0]), clipped_prediction[:,i], marker='o', markersize=1)
plt.xlabel('Time')  # X-axis label
plt.ylabel('Magnitude')  # Y-axis label
plt.title('Prediction');  # title of the plot
plt.show()
