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
    # Runs normalized cross correlation function (NCCF) on entire audio sample,
    # outputting a set of potential F0 candidates that could be used to
    # determine the pitch at each given frame of the audio sample.

    # TODO: Make these optional params that default to below values:
    # Value of "F0_max" in NCCF equation:
    maximum_allowed_freq = 500
    # Value of "F0_min" in NCCF equation:
    minimum_allowed_freq = 50
    # Value of "t" in NCCF equation:
    frame_step_size = 0.01
    # Value of "w" in NCCF equation:
    correlation_window_size = 0.0075

    # Value of "n" in NCCF equation:
    samples_correlated_per_lag = int(correlation_window_size * sample_rate)

    # starting value for "k" in NCCF equation
    shortest_lag_per_frame = int(sample_rate / maximum_allowed_freq)

    # Value of "K" in NCCF equation
    longest_lag_per_frame = int(sample_rate / minimum_allowed_freq)

    # Value of "z" in NCCF equation
    samples_per_frame = int(frame_step_size * sample_rate)

    # Value of "M" in NCCF equation
    max_frame_count = int(len(audio_input) / samples_per_frame)

    lag_range = longest_lag_per_frame - shortest_lag_per_frame

    # TODO: Re-read discussion of using double-precision arithmetic in 3.3
    candidates = numpy.zeros((max_frame_count, lag_range))
    for i in xrange(0, max_frame_count):
        for k in xrange(0, lag_range):
            samples = 0
            for j in xrange(0, samples_correlated_per_lag - 1):
                correlated_samples = _get_samples(audio_input, i, j,
                                                  samples_per_frame,
                                                  samples_correlated_per_lag,
                                                  longest_lag_per_frame)
                samples_for_lag = _get_samples(audio_input, i, j + k,
                                               samples_per_frame,
                                               samples_correlated_per_lag,
                                               longest_lag_per_frame)
                samples += correlated_samples * samples_for_lag
                candidates[i][k] = samples

    return candidates


def _get_samples(audio_input, frame_index, correlation_index, samples_per_frame,
                 samples_correlated_per_lag, longest_lag_per_frame):
    # For a given frame, take non-zero mean of the samples in that frame, and
    # subtract the local mean in the current reference window

    # Value of "s_i,j" in NCCF queation:
    returned_signal = 0

    # Value of "m" in NCCF equation (m = iz) + j
    frame_start = frame_index * samples_per_frame
    # Value of "m+j" in NCCF equation
    start_sample = frame_start + correlation_index
    # end of the frame
    end_sample = start_sample + samples_per_frame
    # value of "x_m+j" in NCCF equation
    mean_for_frame = numpy.mean(audio_input[start_sample:end_sample])
    # value of "m + n - 1"
    last_sample_in_frame = frame_start + samples_correlated_per_lag - 1
    sum_frame_samples = sum(audio_input[start_sample:last_sample_in_frame])
    # value of "u_i" in NCCF equation
    mean_for_window = (1 / samples_correlated_per_lag) * sum_frame_samples

    returned_signal = mean_for_frame - mean_for_window

    return returned_signal
