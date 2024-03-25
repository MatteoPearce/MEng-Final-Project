import timesynth as ts
import numpy as np
import matplotlib.pyplot as plt

def GenerateTimeseries(series_name: str = None, stop_time: int = None) -> np.ndarray:

    time_sampler = ts.TimeSampler(stop_time=500)
    times = time_sampler.sample_regular_time(resolution=1.)

    narma_signal = ts.signals.NARMA(order=10)
    series = ts.TimeSeries(narma_signal)
    samples, signals, errors = series.sample(times)

    plt.plot(times, samples, marker='o', markersize=2)
    plt.xlabel('Time')  # X-axis label
    plt.ylabel('Magnitude')  # Y-axis label
    plt.title('10th-order NARMA Series');  # title of the plot
    plt.show()

    return samples

####GenerateTimeseries()