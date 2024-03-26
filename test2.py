import reservoirpy as rpy
from reservoirpy.nodes import Ridge, Input
from reservoirpy import observables as robs
import numpy as np
from ExtractReservoirOutput import ExtractReservoirIO as ERO
import matplotlib.pyplot as plt
np.set_printoptions(threshold=np.inf)

output_node = Ridge(output_dim = 100, name = "output_node ")
#input_node = Input(name = "input_node ")
#model = input_node >> output_node

input_array, output_array = ERO("/home/matteo/Desktop/VAMPIRE_WORKDIR/sourcefield.txt",
                                "/home/matteo/Desktop/VAMPIRE_WORKDIR/reservoir_output.txt")
input_array = np.delete(input_array, 0, axis = 0)

scaling_factor = 1

lower_limit = int(0.8 * input_array.shape[0])
upper_limit = input_array.shape[0]

print(np.average(output_array[:800,:] ))

training_y = input_array[:lower_limit,:]
training_X = output_array[:lower_limit,:] * scaling_factor
testing_y = input_array[lower_limit:,:]
testing_X = output_array[lower_limit:upper_limit,:] * scaling_factor

print(np.average(training_X))

fitted_output = output_node.fit(training_X, training_y)

#print(f"ridge params: {fitted_output.params}")
#print(f"ridge hypers: {fitted_output.hypers}")

prediction = fitted_output.run(testing_X)
MSE = robs.mse(testing_y, prediction)
RMSE = robs.rmse(testing_y, prediction)
NRMSE = robs.nrmse(testing_y, prediction)
R_2 = robs.rsquare(testing_y, prediction)

print(f"MSE: {MSE}")
print(f"RMSE: {RMSE}")
print(f"NRMSE: {NRMSE}")
print(f"R_2: {R_2}")

#print(prediction[:,0])
for i in range(30):
    plt.plot(np.arange(prediction.shape[0]), testing_y[:,i], marker='o', markersize=2)#, color='red')
    plt.plot(np.arange(prediction.shape[0]), prediction[:,i], marker='o', markersize=2)
plt.xlabel('Time')  # X-axis label
plt.ylabel('Magnitude')  # Y-axis label
plt.title('Prediction');  # title of the plot
plt.show()
