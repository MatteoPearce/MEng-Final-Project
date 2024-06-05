import matplotlib.pyplot as plt
import numpy as np
import mne

data_path = mne.datasets.sample.data_path()
print(data_path)
meg_path = data_path / "MEG" / "sample"

# Set parameters
raw_fname = meg_path / "sample_audvis_filt-0-40_raw.fif"
raw_fname1 = meg_path / "sub-2218A_ses-0001_task-attnmod_run-01_meg.fif" #https://openneuro.org/datasets/ds004837/versions/1.0.0

# Setup for reading the raw data
raw = mne.io.read_raw_fif(raw_fname, preload=True)
raw1 = mne.io.read_raw_fif(raw_fname1, preload=True)

# Set up pick list: MEG - bad channels (modify to your needs)
raw.info["bads"] += ["MEG 2443"]  # mark bads
#raw1.info['bads'] += ["MEG 2443"]
picks = mne.pick_types(raw.info, meg='mag', eeg=False, exclude='bads')
picks = mne.pick_types(raw1.info, meg='mag', eeg=False, exclude='bads')
# Extract the data and times
data, times = raw[picks, :]
data1, times1 = raw1[picks, :]

# If there are multiple magnetometer channels, calculate the magnitude for each time point
# This assumes data is of shape (n_channels, n_times)
mag_field_magnitude = np.linalg.norm(data, axis=0)
mag_field_magnitude1 = np.linalg.norm(data1, axis=0)

for i in range(len(times)):
    if times[i] >= 1:
        end_time = i
        break

for i in range(len(times1)):
    if times1[i] >= 1:
        start_time1 = i
        break
for i in range(len(times1)):
    if times1[i] >= 2:
        end_time1 = i
        break

first_s = times[:end_time]
first_s_mag = mag_field_magnitude[:end_time]

first_s1 = times1[start_time1:end_time1]
first_s_mag1 = mag_field_magnitude1[start_time1:end_time1]

# Plot the magnetic field magnitude over the first 100 time steps
plt.figure(figsize=(10, 5))
plt.plot(first_s, first_s_mag)
plt.xlabel('Time (s)')
plt.ylabel('Magnetic Field Magnitude (T)')
plt.title('Magnetic Field Magnitude')
plt.show()

# Plot the magnetic field magnitude over the first 100 time steps
plt.figure(figsize=(10, 5))
plt.plot(first_s1, first_s_mag1)
plt.xlabel('Time (s)')
plt.ylabel('Magnetic Field Magnitude (T)')
plt.title('Magnetic Field Magnitude1')
plt.show()


