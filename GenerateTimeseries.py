import timesynth as ts
import numpy as np
import matplotlib.pyplot as plt
import Sourcefield_Filemaker as SF

"""
USES THE TIMESYNTH LIBRARY TO GENERATE NARMA10 SERIES
"""

def generate_timeseries(stop_time: int = None) -> np.ndarray:

    time_sampler = ts.TimeSampler(stop_time=stop_time) # length of timeseries in terms of steps
    times = time_sampler.sample_regular_time(resolution=1.0) # indicate timestep = 1

    narma_signal = ts.signals.NARMA(order=10) # determines NARMA order, in this experiment NARMA10
    series = ts.TimeSeries(narma_signal)
    samples, signals, errors = series.sample(times) # generate NARMA

    samples = samples - np.average(samples) # centres timeseries around y=0

    return samples