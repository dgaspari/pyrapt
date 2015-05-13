"""
This module encapsulates the rapt function, which runs a pitch tracker
based on David Talkin's Robust Algorithm for Pitch Tracking (RAPT).
"""

# import math
import numpy
from scipy.io import wavfile


def rapt(wavfile_path):
    """
    F0 estimator that uses the RAPT algorithm to determine vocal
    pitch in an audio sample.
    """
    # TODO: Flesh out docstring, describe args. Add an array for alg inputs
    # TODO: try/catch around wavfile.read, handle file read problems
    # TODO: validation of input!
    sample_rate, original_audio = wavfile.read(wavfile_path)

    # TODO: Continue to just convert to mono?
    if len(original_audio.shape) > 1:
        original_audio = original_audio[:, 0]/2 + original_audio[:, 1]/2

    # NCCF (normalized cross correlation function) - identify F0 candidates
    period_candidates = run_nccf(original_audio, sample_rate),

    # Dynamic programming - determine voicing state at each period candidate

    # return output of nccf for now
    return period_candidates


def run_nccf(audio_input, sample_rate):
    """
    This function is specified by the RAPT algorithm to scan the
    entirety of the downsampled audio sample for potential period
    candidates using the nccf function
    """
    # TODO: Make these optional params:
    maximum_allowed_freq = 500
    minimum_allowed_freq = 50
    frame_step_size = 0.01
    # correlation_window_size = 0.0075

    # starting value for "k" in NCCF equation
    shortest_lag_per_frame = int(sample_rate / maximum_allowed_freq)

    # Value of "K" in NCCF equation
    longest_lag_per_frame = int(sample_rate / minimum_allowed_freq)

    # Value of "z" in NCCF equation
    samples_per_frame = int(frame_step_size * sample_rate)

    # Value of "M" in NCCF equation
    max_frame_count = int(len(audio_input) / samples_per_frame)

    # Value of "n" in NCCF equation
    # num_samples_per_lag = int(correlation_window_size * sample_rate)

    lag_range = longest_lag_per_frame - shortest_lag_per_frame

    # TODO: Re-read discussion of using double-precision arithmetic in 3.3
    # TODO: adjust formula based on variations in 3.3
    candidates = numpy.zeros((max_frame_count, lag_range))
    for i in xrange(0, max_frame_count):
        for k in xrange(0, lag_range):
            # summation of samples within frame * said sample + lag:
            # value of "m" in NCCF equation:
            # start_sample = i * samples_per_frame
            # sample_sum = 0
            # squared_sum = 0
            # squared_sum_with_lag = 0
            candidates[i][k] = 1
            # TODO: debug through here, figure out array index issues
            # for j in xrange(start_sample,
            #                 start_sample + num_samples_per_lag - 1):
            #   sample_sum += (downsampled_audio[j] * downsampled_audio[j + k])
            #     squared_sum += downsampled_audio[j] ** 2
            #     squared_sum_with_lag += downsampled_audio[j + k] ** 2
            # divided by sqrt e_m * e_m + lag
            # candidates[i][k] = (sample_sum /
            #                     math.sqrt(squared_sum * squared_sum_with_lag))

    return candidates
