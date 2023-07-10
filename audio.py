import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
from scipy.signal import find_peaks
import pandas as pd
import sounddevice as sd

# Type the indices of the false positive notes after running program once to adjust for error in peak detection
# This is necessary for error calculations to be accurate
OMIT_PEAKS = [1, 8, 20]

MAKE_NEW_RECORDING = False
GENERATE_STATS = True

# Reads data, extracts relevant array and sample rate
DATA = read("output.wav")
data_new = [x[0] for x in DATA[1]]
sample_rate = DATA[0]

# Adjust these to indicate the music you intend to play
UPBEAT = 0
# Tppe a float for each note you intend to play:
# Type the number of that note which would be in a beat. 3 = triplets, 4 = sixteenth notes, 2.5 for a 5:2 polyrhythm, etc.
INTENDED_RHYTHM = [3, 3, 3, 3, 3, 3, 3, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 1]
INTENDED_BPM = 150
samples_per_beat = sample_rate / (INTENDED_BPM / 60)

# Make a new recording if parameter is set
if MAKE_NEW_RECORDING:
    FS = 44100
    SECONDS = 6
    print("recording")
    recording = sd.rec(int(SECONDS * FS), samplerate=FS, channels=2)
    sd.wait()
    write("output.wav", FS, recording)

# Adjust these to experiment with how sensitive the program is to notes being played close together
MAX_BPM = 260
MAX_NOTES_PER_BEAT = 6
distance = sample_rate / (MAX_NOTES_PER_BEAT * (MAX_BPM / 60))

# Smooths the data
window_size = round(distance)
data_smooth = pd.Series(data_new).rolling(window_size).max().tolist()

# Finds peaks and generates array
peaks = find_peaks([x[0] for x in DATA[1]], height=0.04, distance=distance)
peaks_smooth = find_peaks(data_smooth, height=0.04, distance=distance)
# Don't ask
peaks_new = (
    [
        x
        for x in peaks[0]
        if any([x - distance < y < x + distance for y in peaks_smooth[0]])
    ],
    [
        y
        for (x, y) in zip(peaks[0], peaks[1]["peak_heights"])
        if any([x - distance < z < x + distance for z in peaks_smooth[0]])
    ],
)
peaks_omit = (
    [val for idx, val in enumerate(peaks_new[0]) if idx not in OMIT_PEAKS],
    [val for idx, val in enumerate(peaks_new[1]) if idx not in OMIT_PEAKS],
)

# Generates timings array from waveform
timings = []
for peak in peaks_omit[0]:
    timings.append(peak - peaks_new[0][0])

# Generates expected timings array
expected_timings = []
total = 0
for note in INTENDED_RHYTHM:
    expected_timings.append(round(total))
    total += samples_per_beat / note

# Generates array indicating tempo
beats = [x for x in range(0, round(len(data_smooth) / samples_per_beat))]

# Generates statistics about your error
if GENERATE_STATS:
    errors = [
        abs(timings[i] - expected_timings[i]) for i in range(len(expected_timings))
    ]
    total_error = sum(errors)
    total_error_beats = total_error / samples_per_beat
    total_error_seconds = total_error_beats / (INTENDED_BPM / 60)
    average_error_beats = total_error_beats / len(expected_timings)
    average_error_seconds = total_error_seconds / len(expected_timings)
    biggest_error = max(errors)
    biggest_error_beats = biggest_error / samples_per_beat
    biggest_error_index = errors.index(biggest_error)

    # Generates strings for plot
    s1 = f"Total error in beats: {round(total_error_beats, 3)}\n"
    s2 = f"Total error in seconds: {round(total_error_seconds, 3)}\n"
    s3 = f"Average error in beats: {round(average_error_beats * 100, 2)}%\n"
    s4 = f"Average error in seconds: {round(average_error_seconds, 3)}\n"
    s5 = f"Biggest error of {round(biggest_error_beats * 100, 2)}% of a beat on note {biggest_error_index + 1}"

# Generates plot
plt.figure()

# Plot wave form with peaks indicated in red
data_smooth = data_smooth[peaks_omit[0][0] :]
peaks_smooth_samples = [x - peaks_omit[0][0] for x in peaks_omit[0]]
plt.plot(data_smooth)
plt.plot(peaks_smooth_samples, peaks_omit[1], "ro")

# Plot timings charted across x-axis with expected timings and vertical bars on beat
for beat in beats:
    plt.axvline((beat + UPBEAT) * samples_per_beat, color="g")
plt.plot(expected_timings, [-0.2] * len(expected_timings), "b|")
plt.plot(timings, [-0.1] * len(timings), "r|")

if GENERATE_STATS:
    plt.text(0.5, 1.05, s1 + s2 + s3 + s4 + s5, fontsize="x-small")
plt.ylim(top=1, bottom=-1)
plt.show()
