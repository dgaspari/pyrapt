"""
This module encapsulates the rapt function, which runs a pitch tracker
based on David Talkin's Robust Algorithm for Pitch Tracking (RAPT).
"""

import math
# import numpy
from scipy import signal
from scipy.io import wavfile

import raptparams
import nccfparams


def rapt(wavfile_path, **kwargs):
    """
    F0 estimator inspired by RAPT algorithm to determine vocal
    pitch of an audio sample.
    """
    # Process optional keyword args and build out rapt params
    params = _setup_rapt_params(kwargs)

    # TODO: Flesh out docstring, describe args, expected vals in kwargs
    original_audio = _get_audio_data(wavfile_path)

    downsampled_audio = _get_downsampled_audio(original_audio,
                                               params.maximum_allowed_freq)

    first_pass = _run_nccf(downsampled_audio, original_audio, params)

    # NCCF (normalized cross correlation function) - identify F0 candidates
    # TODO: Determine if we want to preprocess audio before NCCF
    # first_pass, max_cor = _first_pass_nccf(downsampled_audio, downsampling_ra
    # first_pass is the theta_i,k and max_cor is theta_max from the results
    # period_candidates = _second_pass_nccf(audio_sample, sample_rate,
    #                                        first_pass, max_cor)

    # Dynamic programming - determine voicing state at each period candidate

    # return output of nccf for now
    return first_pass


def _setup_rapt_params(kwargs):
    # Use optional args for RAPT parameters otherwise use defaults
    params = raptparams.Raptparams()
    if kwargs is not None and isinstance(kwargs, dict):
        for key, value in kwargs.iteritems():
            if key == 'maximum_allowed_freq':
                params.maximum_allowed_freq = value
            if key == 'minimum_allowed_freq':
                params.minimum_allowed_freq = value
            if key == 'frame_step_size':
                params.frame_step_size = value
            if key == 'correlation_window_size':
                params.correlation_window_size = value
            if key == 'max_hypotheses_per_frame':
                params.max_hypotheses_per_frame = value
            if key == 'min_acceptable_peak_val':
                params.min_acceptable_peak_val = value

    return params


def _get_audio_data(wavfile_path):
    # Read wavfile and convert to mono
    sample_rate, audio_sample = wavfile.read(wavfile_path)

    # TODO: investigate whether this type of conversion to mono is suitable:
    if len(audio_sample.shape) > 1:
        audio_sample = audio_sample[:, 0]/2.0 + audio_sample[:, 1]/2.0
        audio_sample = audio_sample.astype(int)

    return (sample_rate, audio_sample)


def _get_downsampled_audio(original_audio, maximum_allowed_freq):
    """
    Calc downsampling rate, downsample audio, return as tuple
    """
    downsample_rate = _calculate_downsampling_rate(original_audio[0],
                                                   maximum_allowed_freq)
    downsampled_audio = _downsample_audio(original_audio, downsample_rate)
    return (downsample_rate, downsampled_audio)


def _downsample_audio(original_audio, downsampling_rate):
    """
    Given the original audio sample/rate and a desired downsampling
    rate, returns a downsampled version of the audio input.
    """
    # TODO: look into applying low pass filter prior to downsampling, as
    # suggested in rapt paper.
    try:
        sample_rate_ratio = float(downsampling_rate) / float(original_audio[0])
    except ZeroDivisionError:
        raise ValueError('Input audio sampling rate is zero. Cannot determine '
                         'downsampling ratio.')
    # resample audio so it only uses a fraction of the original # of samples:
    number_of_samples = len(original_audio[1]) * sample_rate_ratio
    downsampled_audio = signal.resample(original_audio[1], number_of_samples)

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
        raise ValueError('Ratio of sampling rate and max F0 leads to '
                         'division by zero. Cannot perform 1st pass of nccf '
                         'on downsampled audio.')
    return int(aReturn)

# NCCF Functionality:
# TODO: Consider moving nccf functions into a separate module / file?


def _run_nccf(downsampled_audio, original_audio, params):
    first_pass = _first_pass_nccf(downsampled_audio, params)

    # run second pass
    second_pass = _second_pass_nccf(original_audio, first_pass, params)

    return second_pass


def _first_pass_nccf(audio, params):
    # Runs normalized cross correlation function (NCCF) on downsampled audio,
    # outputting a set of potential F0 candidates that could be used to
    # determine the pitch at each given frame of the audio sample.

    nccfparam = _get_nccf_params(audio, params, True)

    # Difference between "K-1" and starting value of "k"
    lag_range = ((nccfparam.longest_lag_per_frame - 1) -
                 nccfparam.shortest_lag_per_frame)

    # TODO: Re-read discussion of using double-precision arithmetic in rapt 3.3

    # NOTE: Because we are using max_frame_count exclusively for array size,
    # we do not run into issues with using xrange to iterate thru each frame, i

    candidates = [None] * nccfparam.max_frame_count

    for i in xrange(0, nccfparam.max_frame_count):
        candidates[i] = _get_firstpass_frame_results(
            audio, i, lag_range, nccfparam, params)

    return candidates


def _second_pass_nccf(original_audio, first_pass, params):
    # Runs NCCF on original audio, but only for lags highlighted from first
    # pass results. Will output the finalized F0 candidates for each frame

    nccfparam = _get_nccf_params(original_audio, params, False)

    # Difference between "K-1" and the starting value of "k"
    lag_range = ((nccfparam.longest_lag_per_frame - 1) -
                 nccfparam.shortest_lag_per_frame)

    candidates = [None] * nccfparam.max_frame_count

    for i in xrange(0, nccfparam.max_frame_count):
        candidates[i] = _get_secondpass_frame_results(
            original_audio, i, lag_range, nccfparam, params, first_pass)

    return candidates


def _get_nccf_params(audio_input, raptparams, is_firstpass):
    """
    Creates and returns nccfparams object w/ nccf-specific values
    """
    nccfparam = nccfparams.Nccfparams()
    # Value of "n" in NCCF equation:
    nccfparam.samples_correlated_per_lag = int(
        raptparams.correlation_window_size * audio_input[0])
    # Starting value of "k" in NCCF equation:
    if(is_firstpass):
        nccfparam.shortest_lag_per_frame = int(audio_input[0] /
                                               raptparams.maximum_allowed_freq)
    else:
        nccfparam.shortest_lag_per_frame = 0
    # Value of "K" in NCCF equation
    nccfparam.longest_lag_per_frame = int(audio_input[0] /
                                          raptparams.minimum_allowed_freq)
    # Value of "z" in NCCF equation
    nccfparam.samples_per_frame = int(raptparams.frame_step_size *
                                      audio_input[0])
    # Value of "M-1" in NCCF equation:
    nccfparam.max_frame_count = (int(float(len(audio_input[1])) /
                                 float(nccfparam.samples_per_frame)) - 1)
    return nccfparam


def _get_firstpass_frame_results(audio, current_frame, lag_range,
                                 nccfparam, raptparam):
    # calculate correlation (theta) for all lags, and get the highest
    # correlation val (theta_max) from the calculated lags:
    all_lag_results = _get_correlations_for_all_lags(audio, current_frame,
                                                     lag_range, nccfparam)

    marked_values = _get_marked_firstpass_results(all_lag_results, raptparam,
                                                  nccfparam)
    return marked_values


def _get_secondpass_frame_results(audio, current_frame, lag_range, nccfparam,
                                  raptparam, first_pass):
    return first_pass[0]


def _get_correlations_for_all_lags(audio, current_frame, lag_range, nccfparam):
    # Value of theta_max in NCCF equation, max for the current frame
    candidates = [0.0] * lag_range
    max_correlation_val = 0.0
    for k in xrange(0, lag_range):
        current_lag = k + nccfparam.shortest_lag_per_frame

        # determine if the current lag value causes us to go past the
        # end of the audio sample - if so - skip and set val to 0
        if ((current_lag + (nccfparam.samples_correlated_per_lag - 1)
             + (current_frame * nccfparam.samples_per_frame)) >= audio[1].size):
            # candidates[k] = 0.0
            # TODO: Verify this behavior in unit test - no need to set val
            # since 0.0 is default
            continue

        candidates[k] = _get_correlation(audio, current_frame,
                                         current_lag, nccfparam)

        if candidates[k] > max_correlation_val:
            max_correlation_val = candidates[k]

    return (candidates, max_correlation_val)


def _get_marked_firstpass_results(lag_results, raptparam, nccfparam):
    # values that meet certain threshold shall be marked for consideration
    min_valid_correlation = (lag_results[1] * raptparam.min_acceptable_peak_val)
    max_allowed_candidates = raptparam.max_hypotheses_per_frame - 1

    candidates = []
    for k, k_val in enumerate(lag_results[0]):
        current_lag = k + nccfparam.shortest_lag_per_frame
        if k_val >= min_valid_correlation:
            candidates.append((current_lag, k_val))

    # now check to see if selected candidates exceed max allowed:
    if len(candidates) > max_allowed_candidates:
        candidates.sort(key=lambda tup: tup[1], reverse=True)
        returned_candidates = candidates[0:max_allowed_candidates]
    else:
        returned_candidates = candidates

    return returned_candidates


def _get_correlation(audio, frame, lag, nccfparam):
    samples = 0
    # NOTE: NCCF formula has inclusive summation from 0 to n-1, but must add
    # 1 to max value here due to standard behavior of range/xrange:
    for j in xrange(0, nccfparam.samples_correlated_per_lag):
        correlated_samples = _get_sample(audio, frame, j, nccfparam)
        samples_for_lag = _get_sample(audio, frame, j + lag, nccfparam)
        samples += correlated_samples * samples_for_lag

    denominator = _get_nccf_denominator_val(audio, frame, 0, nccfparam)

    denominator *= _get_nccf_denominator_val(audio, frame, lag, nccfparam)

    return float(samples) / float(denominator)


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


def _get_sample(audio, frame, correlation_index, nccfparam):
    returned_signal = 0
    # value of "m" in NCCF equation (m=iz)
    frame_start = frame * nccfparam.samples_per_frame
    # value of "m+j" in NCCF equation
    current_sample_index = frame_start + correlation_index
    # value of "x_m+j" in NCCF equation
    current_sample = audio[1][current_sample_index]
    # value of "m + n - 1"
    last_sample_in_frame = frame_start + nccfparam.samples_correlated_per_lag

# summation of samples from "m" to "m+n-1"
    # sum_frame_samples = sum(audio[1][frame_start:last_sample_in_frame])
    frame_sample_sum = 0.0
    for j in xrange(frame_start, last_sample_in_frame):
        frame_sample_sum += audio[1][j]
    # value of "u_i" in NCCF equation
    mean_for_window = ((float(1.0)
                       / float(nccfparam.samples_correlated_per_lag))
                       * frame_sample_sum)

    returned_signal = current_sample - mean_for_window

    return returned_signal


def _get_nccf_denominator_val(audio, frame, starting_val, nccfparam):
    # Calculates the denominator value of the NCCF equation
    # (e_j in the formula)
    total_sum = 0.0
    # NOTE that I am adding 1 to the xrange to be inclusive:
    for l in xrange(starting_val,
                    starting_val + nccfparam.samples_correlated_per_lag):
        sample = float(_get_sample(audio, frame, l, nccfparam))
        total_sum += math.pow(sample, 2)
    return total_sum
