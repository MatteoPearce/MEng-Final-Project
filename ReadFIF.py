import matplotlib.pyplot as plt
import numpy as np
import mne

data_path = mne.datasets.sample.data_path()
print(data_path)
meg_path = data_path / "MEG" / "sample"

# Set parameters
raw_fname = meg_path / "sample_audvis_filt-0-40_raw.fif"

# Setup for reading the raw data
raw = mne.io.read_raw_fif(raw_fname, preload=True)

# Set up pick list: MEG - bad channels (modify to your needs)
raw.info["bads"] += ["MEG 2443"]  # mark bads
picks = mne.pick_types(raw.info, meg='mag', eeg=False, exclude='bads')
# Extract the data and times
data, times = raw[picks, :]

# If there are multiple magnetometer channels, calculate the magnitude for each time point
# This assumes data is of shape (n_channels, n_times)
mag_field_magnitude = np.linalg.norm(data, axis=0)

for i in range(len(times)):
    if times[i] >= 1:
        end_time = i
        break

first_s = times[:end_time]
first_s_mag = mag_field_magnitude[:end_time]

# Plot the magnetic field magnitude over the first 100 time steps
plt.figure(figsize=(10, 5))
plt.plot(first_s, first_s_mag)
plt.xlabel('Time (s)')
plt.ylabel('Magnetic Field Magnitude (T)')
plt.title('Magnetic Field Magnitude over the First 100 Time Steps')
plt.show()


