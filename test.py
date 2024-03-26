from ExtractReservoirOutput import ExtractReservoirIO as ERO
from sklearn import preprocessing
import NeuronOutput
import numpy as np

input_array, output_array = ERO("/home/matteo/Desktop/VAMPIRE_WORKDIR/sourcefield.txt","/home/matteo/Desktop/VAMPIRE_WORKDIR/reservoir_output.txt")
#print(input_array.shape)
np.set_printoptions(threshold=np.inf)
#print(output_array)#[0:102,:])

#np.seterr(all='warn')

input_array = np.delete(input_array, 0, axis = 0)
diff = output_array.shape[0] - input_array.shape[0]
#print(diff)
input_array = np.pad(input_array,((0, diff),(0, 0)))
#output_array = output_array + 10e18
#print(input_array)

#X_normalized = preprocessing.normalize(output_array, norm='ls')
#y_normalized = preprocessing.normalize(input_array, norm='l2')

#print(X_normalized)

model = NeuronOutput.NeuronOutput(reservoir_input=input_array,reservoir_output=output_array,CV=True) #[1000:2000,:]
print(model.score)
print(model.model_params)
print(model.model.predict(input_array)-output_array)
