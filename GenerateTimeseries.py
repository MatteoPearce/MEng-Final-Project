import numpy as np
from matplotlib import pyplot as plt
"""
GENERATE NARMA10 SERIES
"""

def generate_timeseries(stop_time: int = None) -> (np.ndarray, np.ndarray):
    Lag = 0
    while True:
        # generate input
        u = 0.5 * np.random.uniform(low=-1, high=1, size=(stop_time+1000))

        # generate output arrays
        y_base = np.zeros(shape=(stop_time+1000))
        y = np.zeros(shape=(stop_time, Lag+1))

        # calculate intermediate output
        for i in range(10, stop_time+1000):
            # implementation of a tenth order system model
            y_base[i] = 0.3 * y_base[i-1] + 0.05 * y_base[i-1] * \
                np.sum(y_base[i-10:i]) + 1.5 * u[i-1] * u[i-10] + 0.1

        # throw away the first 1000 values (random number), since we need
        # to allow the system to "warum up"
        u = u[1000:]

        # for the default case (Lag = 0), throw away the first 1000 values as
        # well, so we have pairs of u and y values.
        # for Lag > 0,  take earlier values (because of the lag), to be more
        # precise, "value(Lag) earlier values"; do that for every value
        # from 0 to Lag
        for curr_Lag in range(0, Lag+1):
            y[:, curr_Lag] = y_base[1000 - curr_Lag : len(y_base)-curr_Lag]

        # if all values of y are finite, return them with the corresponding
        # inputs
        if np.isfinite(y).all():
            return (u, y)
