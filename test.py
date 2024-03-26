from ExtractReservoirOutput import ExtractReservoirIO as ERO
import NeuronOutput
import numpy as np

input_array, output_array = ERO("/home/matteo/Desktop/VAMPIRE_WORKDIR/sourcefield.txt","/home/matteo/Desktop/VAMPIRE_WORKDIR/reservoir_output.txt")
print(input_array.shape)
print(output_array.shape)
#model = NeuronOutput.NeuronOutput()
