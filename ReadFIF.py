# https://www.dropbox.com/s/q58whpso2jt9tx0/Fiff.pdf?dl=0
#https://openneuro.org/datasets/ds004837/versions/1.0.0
import mne #https://github.com/mne-tools/mne-python/blob/main/tutorials/raw/10_raw_overview.py

path = "/home/matteo/Downloads/raw.fif"

raw = mne.io.read_raw_fif(path)
raw.crop(tmax=60).load_data()
raw.plot()
raw.plot_sensors(ch_type="eeg")

n_time_samps = raw.n_times
time_secs = raw.times
ch_names = raw.ch_names
n_chan = len(ch_names)  # note: there is no raw.n_channels attribute
print(
    f"the (cropped) sample data object has {n_time_samps} time samples and "
    f"{n_chan} channels."
)
print(f"The last time sample is at {time_secs[-1]} seconds.")
print("The first few channel names are {}.".format(", ".join(ch_names[:3])))
print()  # insert a blank line in the output

# some examples of raw.info:
print("bad channels:", raw.info["bads"])  # chs marked "bad" during acquisition
print(raw.info["sfreq"], "Hz")  # sampling frequency
print(raw.info["description"], "\n")  # miscellaneous acquisition info

print(raw.info)