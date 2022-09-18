import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
from scipy.signal import find_peaks
import pandas as pd
import sounddevice as sd

# FS = 44100
# SECONDS = 5
# print("recording")
# recording = sd.rec(int(SECONDS * FS), samplerate=FS, channels=2)
# sd.wait()
# write('output.wav', FS, recording)

DATA = read('output.wav')
data_new = [x[0] for x in DATA[1]]
sample_rate = DATA[0]

MAX_BPM = 260
MAX_NOTES_PER_BEAT = 6
distance = sample_rate / (MAX_NOTES_PER_BEAT * (MAX_BPM / 60))

UPBEAT = 0
INTENDED_RHYTHM = [3, 3, 3, 3, 3, 3, 3, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 1]
INTENDED_BPM = 150
samples_per_beat = sample_rate / (INTENDED_BPM / 60)

window_size = round(distance)
data_smooth = pd.Series(data_new).rolling(
    window_size).max().tolist()

peaks = find_peaks([x[0] for x in DATA[1]], height=.05, distance=distance)
peaks_smooth = find_peaks(data_smooth, height=.05, distance=distance)
# Don't ask
peaks_new = ([x for x in peaks[0] if any(
    [y in range(round(x - distance), round(x + distance)) for y in peaks_smooth[0]])], peaks[1])

timings = []
for peak in peaks_new[0]:
    timings.append(peak - peaks_new[0][0])

expected_timings = []
total = 0
for note in INTENDED_RHYTHM:
    expected_timings.append(round(total))
    total += samples_per_beat / note

beats = [
    x for x in range(0, round(len(data_smooth) / samples_per_beat))]

errors = [abs(timings[i] - expected_timings[i])
          for i in range(len(expected_timings))]
total_error = sum(errors)
total_error_beats = total_error / samples_per_beat
total_error_seconds = total_error_beats / (INTENDED_BPM / 60)
average_error_beats = total_error_beats / len(expected_timings)
average_error_seconds = total_error_seconds / len(expected_timings)
biggest_error = max(errors)
biggest_error_beats = biggest_error / samples_per_beat
biggest_error_index = errors.index(biggest_error)

s1 = f'Total error in beats: {round(total_error_beats, 3)}\n'
s2 = f'Total error in seconds: {round(total_error_seconds, 3)}\n'
s3 = f'Average error in beats: {round(average_error_beats * 100, 2)}%\n'
s4 = f'Average error in seconds: {round(average_error_seconds, 3)}\n'
s5 = f'Biggest error of {round(biggest_error_beats * 100, 2)}% of a beat on note {biggest_error_index + 1}'


plt.figure()

# Plot wave form with peaks indicated in red
data_smooth = data_smooth[peaks_new[0][0]:]
peaks_smooth_samples = [x - peaks_new[0][0] for x in peaks_new[0]]
plt.plot(data_smooth)
plt.plot(peaks_smooth_samples,
         peaks_new[1]['peak_heights'], 'ro')

# Plot timings charted across x-axis with expected timings and vertical bars on beat
for beat in beats:
    plt.axvline((beat + UPBEAT) * samples_per_beat, color='g')
plt.plot(expected_timings,
         [-.2] * len(expected_timings), 'b|')
plt.plot(timings, [-.1] * len(timings), 'r|')

plt.text(.5, 1.05, s1 + s2 + s3 + s4 + s5, fontsize='x-small')
plt.ylim(top=1, bottom=-1)
plt.show()
