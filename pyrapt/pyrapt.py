"""
This module encapsulates the rapt function, which runs a pitch tracker
based on David Talkin's Robust Algorithm for Pitch Tracking (RAPT).
"""

# import math
import numpy
from scipy.io import wavfile


def rapt(wavfile_path):
    """
    F0 estimator inspired by RAPT algorithm to determine vocal
    pitch of an audio sample.
    """
    # TODO: Flesh out docstring, describe args. Add an array for alg inputs
    sample_rate, audio_sample = _get_audio_data(wavfile_path)

    # NCCF (normalized cross correlation function) - identify F0 candidates
    # TODO: Determine if we want to preprocess audio before NCCF
    period_candidates = _run_nccf(audio_sample, sample_rate),

    # Dynamic programming - determine voicing state at each period candidate

    # return output of nccf for now
    return period_candidates


def _get_audio_data(wavfile_path):
    # Read wavfile and convert to mono
    sample_rate, audio_sample = wavfile.read(wavfile_path)

    # TODO: investigate whether this type of conversion to mono is suitable:
    if len(audio_sample.shape) > 1:
        audio_sample = audio_sample[:, 0]/2.0 + audio_sample[:, 1]/2.0
        audio_sample = audio_sample.astype(int)

    return sample_rate, audio_sample


def _run_nccf(audio_input, sample_rate):
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
