"""
This module encapsulates the rapt function, which runs an implementation
of David Talkin's Robust Algorithm for Pitch Tracking (RAPT).
"""

import math
import numpy
from scipy import signal
from scipy.io import wavfile


def rapt(wavfile_path):
    """
    F0 estimator that uses the RAPT algorithm to determine vocal
    pitch in an audio sample.
    """
    # TODO: Flesh out docstring, describe args. Add an array for alg inputs
    # TODO: try/catch around wavfile.read, handle file read problems
    sample_rate, original_audio = wavfile.read(wavfile_path)

    # TODO: Continue to just convert to mono?
    if len(original_audio.shape) > 1:
        original_audio = original_audio[:, 0]/2 + original_audio[:, 1]/2

    # TODO: pass max F0 from alg param list to calc downsampling rate method
    downsampling_rate = calculate_downsampling_rate(sample_rate, 500)
    downsampled_audio = downsample_audio(original_audio,
                                         sample_rate, downsampling_rate)

    # Next we need to run NCCF on the downsampled audio
    # TODO: pass other input args into nccf call
    first_pass_results = nccf_first_pass(downsampled_audio,
                                         downsampling_rate, sample_rate)

    # Based on the output of the 1st pass, examine the notable maxima

    # Dynamic programming - determine voicing state at each period candidate

    return first_pass_results


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
        raise ValueError('Ratio of sampling rate and max F0 leads to '
                         'division by zero. No 1st pass of downsampled '
                         'audio should occur.')
    return int(aReturn)


def downsample_audio(original_audio, sample_rate, downsampling_rate):
    """
    Given the original audio sample/rate and a desired downsampling
    rate, returns a downsampled version of the audio input.
    """
    sample_rate_ratio = float(downsampling_rate) / float(sample_rate)
    downsampled_audio = signal.resample(original_audio,
                                        len(original_audio) * sample_rate_ratio)
    return downsampled_audio


def nccf_first_pass(downsampled_audio, downsampling_rate, sample_rate):
    """
    This function is used by the RAPT algorithm to scan the entirety
    of the downsampled audio sample for potential period candidates
    using the nccf function
    """
    # TODO: Make these optional params:
    maximum_allowed_freq = 500
    minimum_allowed_freq = 50
    frame_step_size = 0.01
    correlation_window_size = 0.0075

    # starting value for "k" in NCCF equation
    shortest_lag_per_frame = int(downsampling_rate / maximum_allowed_freq)

    # Value of "K" in NCCF equation
    longest_lag_per_frame = int(downsampling_rate / minimum_allowed_freq)

    # Value of "z" in NCCF equation
    samples_per_frame = int(frame_step_size * downsampling_rate)

    # Value of "M" in NCCF equation
    max_frame_count = int(len(downsampled_audio) / samples_per_frame)

    # Value of "n" in NCCF equation
    num_samples_per_lag = int(correlation_window_size * downsampling_rate)

    lag_range = longest_lag_per_frame - shortest_lag_per_frame

    # TODO: Re-read discussion of using double-precision arithmetic in 3.3
    # TODO: adjust formula based on variations in 3.3
    candidates = numpy.zeros((max_frame_count, lag_range))
    for i in xrange(0, max_frame_count):
        for k in xrange(0, lag_range):
            # summation of samples within frame * said sample + lag:
            # value of "m" in NCCF equation:
            start_sample = i * samples_per_frame
            sample_sum = 0
            squared_sum = 0
            squared_sum_with_lag = 0
            # TODO: debug through here, figure out array index issues
            # for j in xrange(start_sample,
            #                 start_sample + num_samples_per_lag - 1):
            #     sample_sum += (downsampled_audio[j] * downsampled_audio[j + k])
            #     squared_sum += downsampled_audio[j] ** 2
            #     squared_sum_with_lag += downsampled_audio[j + k] ** 2
            # divided by sqrt e_m * e_m + lag
            # candidates[i][k] = (sample_sum /
            #                     math.sqrt(squared_sum * squared_sum_with_lag))

    return candidates
