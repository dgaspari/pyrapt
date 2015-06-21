"""
Unit tests for methods used during NCCF calculations
"""
from unittest import TestCase
from mock import patch

import numpy

from pyrapt import pyrapt
from pyrapt import raptparams
from pyrapt import nccfparams


class TestNccfMethods(TestCase):

    @patch('pyrapt.pyrapt._first_pass_nccf')
    def test_run_nccf(self, mock_first_pass):
        mock_first_pass.return_value = [([0.2] * 35, 0.3)] * 166
        downsampled_audio = (10, numpy.array([0, 1, 2, 3]))
        original_audio = (100, numpy.array([0, 1, 2, 3, 4, 5, 6]))
        params = raptparams.Raptparams()
        results = pyrapt._run_nccf(downsampled_audio, original_audio, params)
        self.assertEqual(166, len(results))
        self.assertEqual(35, len(results[0][0]))
        self.assertEqual(0.3, results[165][1])

    def test_get_nccfparams(self):
        audio_input = (10, numpy.zeros(60))
        params = raptparams.Raptparams()
        params.correlation_window_size = 2.0
        params.minimum_allowed_freq = 2.0
        params.maximum_allowed_freq = 2.0
        params.frame_step_size = 2.0
        first_params = pyrapt._get_nccf_params(audio_input, params, True)
        self.assertEqual(20, first_params.samples_correlated_per_lag)
        self.assertEqual(5, first_params.shortest_lag_per_frame)
        self.assertEqual(5, first_params.longest_lag_per_frame)
        self.assertEqual(20, first_params.samples_per_frame)
        self.assertEqual(2, first_params.max_frame_count)
        second_params = pyrapt._get_nccf_params(audio_input, params, False)
        self.assertEqual(0, second_params.shortest_lag_per_frame)
        self.assertEqual(5, second_params.longest_lag_per_frame)
        self.assertEqual(20, second_params.samples_correlated_per_lag)
        self.assertEqual(2, second_params.max_frame_count)

    @patch('pyrapt.pyrapt._get_firstpass_frame_results')
    def test_nccf_return_dimensions(self, mock_frame_results):
        mock_frame_results.return_value = [0.0] * 35, 0.5
        # TODO: This is with default params. Do it with passed in ones as well
        sample_rate = 2004
        audio_data = numpy.full(3346, 5.0)
        params = raptparams.Raptparams()
        candidates = pyrapt._first_pass_nccf((sample_rate, audio_data), params)
        self.assertEqual(166, len(candidates))
        self.assertEqual(35, len(candidates[0][0]))
        self.assertEqual(0.5, candidates[34][1])

    @patch('pyrapt.pyrapt._get_correlations_for_all_lags')
    def test_get_results_for_frame(self, mock_get_for_all_lags):
        mock_get_for_all_lags.return_value = ([0.2] * 35, 0.3)
        audio = (2004, numpy.full(3346, 5.0))
        params = nccfparams.Nccfparams()
        params.samples_correlated_per_lag = 20
        params.samples_per_frame = 20
        params.shortest_lag_per_frame = 10
        lag_range = 8
        results = pyrapt._get_firstpass_frame_results(audio, 5,
                                                      lag_range, params)
        self.assertEqual(35, len(results[0]))
        self.assertEqual(0.3, results[1])

    # TODO: test logic where we avoid lags that exceed sample array len
    @patch('pyrapt.pyrapt._get_correlation')
    def test_get_correlations_for_all_lags(self, mock_get_correlation):
        mock_get_correlation.return_value = 0.4
        audio = (2004, numpy.full(3346, 5.0))
        params = nccfparams.Nccfparams()
        params.samples_correlated_per_lag = 20
        params.samples_per_frame = 20
        params.shortest_lag_per_frame = 10
        lag_range = 8
        results = pyrapt._get_correlations_for_all_lags(audio, 5,
                                                        lag_range, params)
        self.assertEqual(0.4, results[1])
        self.assertEqual(8, len(results[0]))
        self.assertEqual(0.4, results[0][7])

    # TODO: have variable return values for mocks depending on inputs
    # TODO: verify inputs came in as expected:
    @patch('pyrapt.pyrapt._get_nccf_denominator_val')
    def test_get_correlation(self, mock_denominator):
        audio = (10, numpy.array([0, 1, 2, 3, 4, 5]))
        params = nccfparams.Nccfparams()
        params.samples_correlated_per_lag = 5
        mock_denominator.return_value = 2.0
        with patch('pyrapt.pyrapt._get_sample') as mock_sample:
            mock_sample.return_value = 4.0
            correlation = pyrapt._get_correlation(audio, 0, 0, params)
            self.assertEqual(20.0, correlation)

    def test_get_sample(self):
        param = nccfparams.Nccfparams()
        param.samples_correlated_per_lag = 5
        param.samples_per_frame = 1
        audio_data = (10, numpy.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
        sample = pyrapt._get_sample(audio_data, 1, 5, param)
        self.assertEqual(3.0, sample)

    @patch('pyrapt.pyrapt._get_sample')
    def test_denominator(self, mock_get_signal):
        audio_data = (100, numpy.ones(1000))
        param = nccfparams.Nccfparams()
        param.samples_correlated_per_lag = 4
        mock_get_signal.return_value = 5.0
        returned = pyrapt._get_nccf_denominator_val(audio_data, 0, 1, param)
        self.assertEqual(100.0, returned)
        param.samples_correlated_per_lag = 3
        mock_get_signal.return_value = 2.0
        returned = pyrapt._get_nccf_denominator_val(audio_data, 0, 4, param)
        self.assertEqual(12.0, returned)
