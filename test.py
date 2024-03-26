from ExtractReservoirOutput import ExtractReservoirIO as ERO
from sklearn import preprocessing
import NeuronOutput
import numpy as np
import matplotlib.pyplot as plt

input_array, output_array = ERO("/home/matteo/Desktop/VAMPIRE_WORKDIR/sourcefield.txt","/home/matteo/Desktop/VAMPIRE_WORKDIR/reservoir_output.txt")
#print(input_array.shape)
np.set_printoptions(threshold=np.inf)
#print(output_array)#[0:102,:])

#np.seterr(all='warn')

input_array = np.delete(input_array, 0, axis = 0)
diff = output_array.shape[0] - input_array.shape[0]
#print(diff)
#input_array = np.pad(input_array,((0, diff),(0, 0)))
#output_array = output_array + 10e18
#print(input_array)

training_y = input_array[:800,:]
training_X = output_array[:800,:]
testing_y = input_array[800:,:]
testing_X = output_array[800:,:]

#X_normalized = preprocessing.normalize(output_array, norm='ls')
#y_normalized = preprocessing.normalize(input_array, norm='l2')

#print(X_normalized)

model = NeuronOutput.NeuronOutput(reservoir_input=input_array,reservoir_output=output_array[:1000,:],CV=False) #[1000:2000,:]
print(model.score)
print(model.model_params)

prediction = model.fitted_model.predict(testing_X)
print((prediction.shape))
#prediction = prediction[:200,:]
#error = prediction - testing_y
#errorp = prediction / testing_y
#print(np.average(error))
#print(np.average(errorp))
"""
plt.plot(np.arange(testing_y.shape[0]), testing_y, marker='o', markersize=2, color='red')
plt.plot(np.arange(testing_y.shape[0]), prediction, marker='o', markersize=2)
plt.xlabel('Time')  # X-axis label
plt.ylabel('Magnitude')  # Y-axis label
plt.title('10th-order NARMA Series');  # title of the plot
plt.show()
"""
plt.plot(np.arange(len(prediction.ravel())), prediction.ravel(), marker='o', markersize=2)
plt.xlabel('Time')  # X-axis label
plt.ylabel('error')  # Y-axis label
plt.title('10th-order NARMA Series');  # title of the plot
plt.show()
