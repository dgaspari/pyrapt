"""
This module encapsulates the rapt function, which runs a pitch tracker
based on David Talkin's Robust Algorithm for Pitch Tracking (RAPT).
"""

import math
import numpy
from scipy import signal
from scipy.io import wavfile

import raptparams


def rapt(wavfile_path, **kwargs):
    """
    F0 estimator inspired by RAPT algorithm to determine vocal
    pitch of an audio sample.
    """
    # Process optional keyword args and build out rapt params
    params = _setup_rapt_params(kwargs)

    # TODO: Flesh out docstring, describe args. Add an array for alg inputs
    sample_rate, audio_sample = _get_audio_data(wavfile_path)

    # TODO: pass max F0 from alg param list to calc downsampling rate method
    downsample_rate = _calculate_downsampling_rate(sample_rate,
                                                   params.maximum_allowed_freq)
    downsampled_audio = _downsample_audio(audio_sample, sample_rate,
                                          downsample_rate)

    first_pass, max_cor = _run_nccf(downsampled_audio, downsample_rate,
                                    audio_sample, sample_rate, params)

    # NCCF (normalized cross correlation function) - identify F0 candidates
    # TODO: Determine if we want to preprocess audio before NCCF
    # first_pass, max_cor = _first_pass_nccf(downsampled_audio, downsampling_ra
    # first_pass is the theta_i,k and max_cor is theta_max from the results
    # period_candidates = _second_pass_nccf(audio_sample, sample_rate,
    #                                        first_pass, max_cor)

    # Dynamic programming - determine voicing state at each period candidate

    # return output of nccf for now
    return first_pass, max_cor


def _setup_rapt_params(kwargs):
    # Use optional args for RAPT parameters otherwise use defaults
    params = raptparams.Raptparams()
    if kwargs is not None:
        for key, value in kwargs.iteritems():
            if key == 'maximum_allowed_freq':
                params.maximum_allowed_freq = value
            if key == 'minimum_allowed_freq':
                params.minimum_allowed_freq = value
            if key == 'frame_step_size':
                params.frame_step_size = value
            if key == 'correlation_window_size':
                params.correlation_window_size = value

    return params


def _get_audio_data(wavfile_path):
    # Read wavfile and convert to mono
    sample_rate, audio_sample = wavfile.read(wavfile_path)

    # TODO: investigate whether this type of conversion to mono is suitable:
    if len(audio_sample.shape) > 1:
        audio_sample = audio_sample[:, 0]/2.0 + audio_sample[:, 1]/2.0
        audio_sample = audio_sample.astype(int)

    return sample_rate, audio_sample


def _downsample_audio(original_audio, sample_rate, downsampling_rate):
    """
    Given the original audio sample/rate and a desired downsampling
    rate, returns a downsampled version of the audio input.
    """
    try:
        sample_rate_ratio = float(downsampling_rate) / float(sample_rate)
    except ZeroDivisionError:
        raise ValueError('Input audio sampling rate is zero. Cannot determine '
                         'downsampling ratio.')
    # resample audio so it only uses a fraction of the original # of samples:
    downsampled_audio = signal.resample(original_audio,
                                        len(original_audio) * sample_rate_ratio)
    return downsampled_audio


def _calculate_downsampling_rate(initial_sampling_rate, maximum_f0):
    """
    Determines downsampling rate to apply to the audio input passed for
    RAPT processing
    """

    """
    NOTE: Using Python 2.7 so division is integer division by default
    Different default behavior in in Python 3+. That said, keeping the
    round() around the denominator of this formula as it is specified in
    the formula in David Talkin's paper:
    """
    try:
        aReturn = (initial_sampling_rate /
                   round(initial_sampling_rate / (4 * maximum_f0)))
    except ZeroDivisionError:
        raise ValueError('Ratio of sampling rate and max F0 leads to'
                         'division by zero. No 1st pass of downsampled '
                         'audio should occur.')
    return int(aReturn)

# NCCF Functionality:
# TODO: Consider moving nccf functions into a separate module / file?


def _run_nccf(downsampled_audio, downsampling_rate, original_audio,
              sampling_rate, params):
    first_pass, max_cor = _first_pass_nccf(downsampled_audio,
                                           downsampling_rate, params)

    # run second pass

    return first_pass, max_cor


def _first_pass_nccf(audio_input, sample_rate, params):
    # Runs normalized cross correlation function (NCCF) on downsampled audio,
    # outputting a set of potential F0 candidates that could be used to
    # determine the pitch at each given frame of the audio sample.

    # TODO: Make these optional params that default to below values:
    # Value of "F0_max" in NCCF equation:
    maximum_allowed_freq = params.maximum_allowed_freq
    # Value of "F0_min" in NCCF equation:
    minimum_allowed_freq = params.minimum_allowed_freq
    # Value of "t" in NCCF equation:
    frame_step_size = params.frame_step_size
    # Value of "w" in NCCF equation:
    correlation_window_size = params.correlation_window_size

    # Value of "n" in NCCF equation:
    samples_correlated_per_lag = int(correlation_window_size * sample_rate)

    # starting value for "k" in NCCF equation
    shortest_lag_per_frame = int(sample_rate / maximum_allowed_freq)

    # Value of "K" in NCCF equation
    longest_lag_per_frame = int(sample_rate / minimum_allowed_freq)

    # Value of "z" in NCCF equation
    samples_per_frame = int(frame_step_size * sample_rate)

    # Value of "M-1" in NCCF equation
    max_frame_count = (int(float(len(audio_input)) / float(samples_per_frame)
                       - 1))

    # Difference between "K-1" and starting value of "k"
    lag_range = (longest_lag_per_frame - 1) - shortest_lag_per_frame

    # Value of theta_max in NCCF equation
    max_correlation_val = 0.0

    # TODO: Re-read discussion of using double-precision arithmetic in 3.3
    candidates = numpy.zeros((max_frame_count, lag_range))
    for i in xrange(0, max_frame_count):
        for k in xrange(0, lag_range):
            current_lag = k + shortest_lag_per_frame

            # determine if the current lag value causes us to go past the
            # end of the audio sample - if so - skip and set val to 0
            if ((current_lag + (samples_correlated_per_lag - 1)
                    + (i * samples_per_frame)) >= audio_input.size):
                candidates[i][k] = 0
                continue

            samples = 0
            for j in xrange(0, samples_correlated_per_lag - 1):
                correlated_samples = _get_sample(audio_input, i, j,
                                                 samples_per_frame,
                                                 samples_correlated_per_lag,
                                                 longest_lag_per_frame)
                samples_for_lag = _get_sample(audio_input, i, j + current_lag,
                                              samples_per_frame,
                                              samples_correlated_per_lag,
                                              longest_lag_per_frame)
                samples += correlated_samples * samples_for_lag

            denominator = _get_nccf_denominator_val(audio_input, i, 0,
                                                    samples_per_frame,
                                                    samples_correlated_per_lag,
                                                    longest_lag_per_frame)

            denominator *= _get_nccf_denominator_val(audio_input, i,
                                                     current_lag,
                                                     samples_per_frame,
                                                     samples_correlated_per_lag,
                                                     longest_lag_per_frame)
            candidates[i][k] = float(samples) / float(denominator)
            if candidates[i][k] > max_correlation_val:
                max_correlation_val = candidates[i][k]

    return candidates, max_correlation_val


def _second_pass_nccf(audio_input, sample_rate, first_pass):
    # TODO: Make these optional params that default to below values:
    # Value of "F0_max" in NCCF equation:
    # maximum_allowed_freq = 500
    # Value of "F0_min" in NCCF equation:
    minimum_allowed_freq = 50
    # Value of "t" in NCCF equation:
    frame_step_size = 0.01
    # Value of "w" in NCCF equation:
    correlation_window_size = 0.0075
    # Value of "AFACT" in NCCF equation:
    absolute_frequency_addition = 10000

    # Value of "n" in NCCF equation:
    samples_correlated_per_lag = int(correlation_window_size * sample_rate)

    # starting value for "k" in NCCF equation
    # NOTE: THIS IS ONLY MEANT FOR FIRST PASS, OTHERWISE k STARTS AT ZERO
    # shortest_lag_per_frame = int(sample_rate / maximum_allowed_freq)
    shortest_lag_per_frame = 0

    # Value of "K" in NCCF equation
    longest_lag_per_frame = int(sample_rate / minimum_allowed_freq)

    # Value of "z" in NCCF equation
    samples_per_frame = int(frame_step_size * sample_rate)

    # Value of "M-1" in NCCF equation
    max_frame_count = (int(float(len(audio_input)) / float(samples_per_frame)
                       - 1))

    # Difference between "K-1" and starting value of "k"
    lag_range = (longest_lag_per_frame - 1) - shortest_lag_per_frame

    # TODO: Re-read discussion of using double-precision arithmetic in 3.3
    candidates = numpy.zeros((max_frame_count, lag_range))
    for i in xrange(0, max_frame_count):
        for k in xrange(0, lag_range):
            current_lag = k + shortest_lag_per_frame

            # determine if the current lag value causes us to go past the
            # end of the audio sample - if so - skip and set val to 0
            if ((current_lag + (samples_correlated_per_lag - 1)
                    + (i * samples_per_frame)) >= audio_input.size):
                candidates[i][k] = 0
                continue

            samples = 0
            for j in xrange(0, samples_correlated_per_lag - 1):
                correlated_samples = _get_sample(audio_input, i, j,
                                                 samples_per_frame,
                                                 samples_correlated_per_lag,
                                                 longest_lag_per_frame)
                samples_for_lag = _get_sample(audio_input, i, j + current_lag,
                                              samples_per_frame,
                                              samples_correlated_per_lag,
                                              longest_lag_per_frame)
                samples += correlated_samples * samples_for_lag

            denominator = _get_nccf_denominator_val(audio_input, i, 0,
                                                    samples_per_frame,
                                                    samples_correlated_per_lag,
                                                    longest_lag_per_frame)

            denominator *= _get_nccf_denominator_val(audio_input, i,
                                                     current_lag,
                                                     samples_per_frame,
                                                     samples_correlated_per_lag,
                                                     longest_lag_per_frame)
            denominator += math.sqrt(absolute_frequency_addition)
            candidates[i][k] = float(samples) / float(denominator)

    return candidates

# TODO: at some point start_sample is FURTHER than last_sample_in_frame
# (when calculating denominator). Why is that? we use m + n - 1 for
# last sample in frame but that seems off... so just to be clear, when
# i=165 and k=29, in _get_samples for denominator, we invoke this method w:
# correlation_index of 33, samples_per_Frame = 20, samples_per_lag = 15, K=40
# frame_start: 3300
# start_sample: 3333
# end_sample: 3353
# last_sample_in_frame: 3314 <<< heres the problem
# the mean_for_frame val seems fine, but sum_frame_samples fails because we
# try and calc sum of input from 3333 to 3314


# TODO: Figure out array out of bounds error
def _get_sample(audio_input, frame_index, correlation_index, samples_per_frame,
                samples_correlated_per_lag, longest_lag_per_frame):
    returned_signal = 0
    # value of "m" in NCCF equation (m=iz)
    frame_start = frame_index * samples_per_frame
    # value of "m+j" in NCCF equation
    current_sample_index = frame_start + correlation_index

    # value of "x_m+j" in NCCF equation
    current_sample = audio_input[current_sample_index]
    # value of "m + n - 1"
    last_sample_in_frame = frame_start + samples_correlated_per_lag - 1
    # summation of samples from "m" to "m+n-1"
    sum_frame_samples = sum(audio_input[frame_start:last_sample_in_frame])
    # value of "u_i" in NCCF equation
    mean_for_window = ((float(1.0) / float(samples_correlated_per_lag)) *
                       sum_frame_samples)

    returned_signal = current_sample - mean_for_window

    return returned_signal


def _get_nccf_denominator_val(audio_input, frame_index, starting_val,
                              samples_per_frame, samples_correlated_per_lag,
                              longest_lag_per_frame):
    total_sum = 0.0
    for l in xrange(starting_val,
                    starting_val + samples_correlated_per_lag - 1):
        samples = _get_sample(audio_input, frame_index, l, samples_per_frame,
                              samples_correlated_per_lag,
                              longest_lag_per_frame)
        total_sum += math.pow(2, samples)
    return total_sum
