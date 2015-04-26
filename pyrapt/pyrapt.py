"""
This module defines the Pyrapt class, which encapsulates an
implementation of David Talkin's Robust Algorithm for Pitch Tracking
(RAPT).
"""

from scipy import signal
from scipy.io import wavfile


def calculate_downsampling_rate(initial_sampling_rate, maximum_f0):
    """
    Determines downsampling rate to apply to the audio input passed for
    RAPT processing
    """

    """
    NOTE: Using Python 2.7 so division is integer division by default
    This would behave different in Python 3+. That said, keeping the
    round() around the denominator of this formula as it is specified in
    the formula in David Talkin's paper:
    """
    try:
        aReturn = (initial_sampling_rate /
                   round(initial_sampling_rate / (4 * maximum_f0)))
    except ZeroDivisionError:
        raise ValueError('Ratio of sampling rate and max f_0 leads to '
                         'division by zero. No 1st pass of downsampled '
                         'audio should occur.')
    return round(aReturn)


def _demo(wavfile_path):
    """
    Rough demo of the RAPT alg process - downsampling input audio,
    cross-correlation first pass on downsampled audio, then second pass
    on the original audio. Followed by the dynamic programming steps.
    The logic here will be refined in the rest of class.
    """
    # get audio input data using scipy.io wav reader:
    original_audio = wavfile.read(wavfile_path)
    downsampling_rate = calculate_downsampling_rate(original_audio[0], 500)
    # 2nd arg could be constant configurable - max Fzero
    # downsampled_audio =
    # signal.resample(original_audio[1], int(downsampling_rate))
    # decimate or resample options available here:
    downsampled_audio = signal.decimate(
        original_audio[1], int(downsampling_rate))
    # TODO: need details on lowpass fir filter
    return downsampled_audio
