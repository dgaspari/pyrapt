from pyrapt import pyrapt
# import numpy as np
from matplotlib import pyplot as plt

original_audio = pyrapt._get_audio_data('example.wav')
fig, ax1 = plt.subplots(nrows=1)
data, freqs, bins, im = ax1.specgram(original_audio[1])
ax1.axis('tight')
plt.show()
# fig, (ax1, ax2) = plt.subplots(nrows=2)
# data, freqs, bins, im = ax1.specgram(original_audio[1])
# ax1.axis('tight')
# ax2.pcolormesh(bins, freqs, 10 * np.log10(data))
# ax2.axis('tight')
# plt.show()
