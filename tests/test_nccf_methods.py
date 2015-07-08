"""
Unit tests for methods used during NCCF calculations
"""
from unittest import TestCase
from mock import patch
from mock import ANY

import numpy

from pyrapt import pyrapt
from pyrapt import raptparams
from pyrapt import nccfparams


class TestNccfMethods(TestCase):

    @patch('pyrapt.pyrapt._first_pass_nccf')
    def test_run_nccf(self, mock_first_pass):
        with patch('pyrapt.pyrapt._second_pass_nccf') as mock_second_pass:
            mock_first_pass.return_value = [[(4, 0.6)] * 5] * 166
            mock_second_pass.return_value = [[(4, 0.6)] * 3] * 166
            downsampled_audio = (10, numpy.array([0, 1, 2, 3]))
            original_audio = (100, numpy.array([0, 1, 2, 3, 4, 5, 6]))
            params = raptparams.Raptparams()
            results = pyrapt._run_nccf(downsampled_audio, original_audio,
                                       params)
            mock_first_pass.assert_called_once_with(downsampled_audio, params)
            mock_second_pass.assert_called_once_with(original_audio, ANY,
                                                     params, 10.0)
            self.assertEqual(166, len(results))
            self.assertEqual(4, results[0][0][0])
            self.assertEqual(0.6, results[165][2][1])

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
    def test_nccf_firstpass(self, mock_frame_results):
        mock_frame_results.return_value = [(8, 0.7), (12, 0.8), (21, 0.6)]
        # TODO: This is with default params. Do it with passed in ones as well
        sample_rate = 2004
        audio_data = numpy.full(3346, 5.0)
        params = raptparams.Raptparams()
        candidates = pyrapt._first_pass_nccf((sample_rate, audio_data), params)
        self.assertEqual(166, len(candidates))
        self.assertEqual(3, len(candidates[0]))
        self.assertEqual(0.8, candidates[34][1][1])

    @patch('pyrapt.pyrapt._get_secondpass_frame_results')
    def test_nccf_secondpass(self, mock_frame_results):
        mock_frame_results.return_value = [(5, 0.6), (30, 0.7), (55, 0.9)]
        first_pass = [(4, 0.6), (4, 0.6), (4, 0.6)] * 165
        audio_data = (44100, numpy.full(73612, 6.8))
        raptparam = raptparams.Raptparams()
        with patch('pyrapt.pyrapt._get_nccf_params') as mock_get_params:
            nccfparam = nccfparams.Nccfparams()
            # lag range is supposed to be 0-samplerate/50 for 2nd pass default:
            nccfparam.shortest_lag_per_frame = 0
            nccfparam.longest_lag_per_frame = 882
            nccfparam.max_frame_count = 165
            params = (raptparam, nccfparam)
            mock_get_params.return_value = nccfparam
            candidates = pyrapt._second_pass_nccf(audio_data, first_pass,
                                                  raptparam, 20)
            mock_get_params.assert_called_once_with(audio_data, raptparam,
                                                    False)
            # at each frame we get results, with lag range being max - 1
            mock_frame_results.assert_called_with(audio_data, ANY, 881, params,
                                                  first_pass, 20)
            self.assertEqual(165, len(candidates))
            self.assertEqual(5, candidates[0][0][0])

    @patch('pyrapt.pyrapt._get_correlations_for_all_lags')
    def test_get_results_for_frame(self, mock_get_for_all_lags):
        mock_get_for_all_lags.return_value = ([0.2] * 35, 0.3)
        audio = (2004, numpy.full(3346, 5.0))
        params = (raptparams.Raptparams(), nccfparams.Nccfparams())
        lag_range = 8
        with patch('pyrapt.pyrapt._get_marked_firstpass_results') as mock_mark:
            mock_mark.return_value = [(9, 0.7), (15, 0.8), (17, 0.6)]
            results = pyrapt._get_firstpass_frame_results(audio, 5, lag_range,
                                                          params)
            mock_mark.assert_called_once_with(ANY, ANY)
            self.assertEqual(3, len(results))
            self.assertEqual(0.8, results[1][1])

    @patch('pyrapt.pyrapt._get_correlations_for_input_lags')
    def test_get_second_pass_results_for_frame(self, mock_get_correlations):
        with patch('pyrapt.pyrapt._get_marked_firstpass_results') as mock_res:
            mock_get_correlations.return_value = ([0.2] * 35, 0.5)
            mock_res.return_value = [(4, 0.6), (4, 0.6), (4, 0.6)] * 165
            audio = (44100, numpy.full(73612, 7.3))
            i = 5
            lag_range = 5
            params = (raptparams.Raptparams(), nccfparams.Nccfparams())
            first_pass = [(4, 0.5), (5, 0.6), (22, 0.7)] * 165
            frame_results = pyrapt._get_secondpass_frame_results(audio, i,
                                                                 lag_range,
                                                                 params,
                                                                 first_pass, 20)
            self.assertEqual(4, frame_results[0][0])

    # TODO: test logic where we avoid lags that exceed sample array len
    @patch('pyrapt.pyrapt._get_correlation')
    def test_get_correlations_for_all_lags(self, mock_get_correlation):
        mock_get_correlation.return_value = 0.4
        audio = (2004, numpy.full(3346, 5.0))
        params = (raptparams.Raptparams(), nccfparams.Nccfparams())
        params[1].samples_correlated_per_lag = 20
        params[1].samples_per_frame = 20
        params[1].shortest_lag_per_frame = 10
        lag_range = 8
        results = pyrapt._get_correlations_for_all_lags(audio, 5,
                                                        lag_range, params)
        self.assertEqual(0.4, results[1])
        self.assertEqual(8, len(results[0]))
        self.assertEqual(0.4, results[0][7])
        mock_get_correlation.assert_called_with(ANY, ANY, ANY, ANY)

    @patch('pyrapt.pyrapt._get_correlation')
    def test_get_correlations_for_input_lags(self, mock_get_correlation):
        mock_get_correlation.return_value = 0.8
        audio = (2004, numpy.full(3346, 5.0))
        params = (raptparams.Raptparams(), nccfparams.Nccfparams())
        params[1].samples_correlated_per_lag = 20
        params[1].samples_per_frame = 20
        params[1].shortest_lag_per_frame = 0
        lag_range = 20
        first_pass = [[(8, 0.7)]] * 20
        results = pyrapt._get_correlations_for_input_lags(audio, 5, first_pass,
                                                          lag_range, params)
        mock_get_correlation.assert_called_with(ANY, ANY, 8, ANY, False)
        self.assertEqual(20, len(results[0]))
        self.assertEqual(0.8, results[1])

    def test_get_marked_firstpass_results(self):
        candidates = ([0.7, 0.2, 0.6, 0.8], 1.0)
        params = (raptparams.Raptparams(), nccfparams.Nccfparams())
        params[1].shortest_lag_per_frame = 7
        params[0].min_acceptable_peak_val = 0.5
        params[0].max_hypotheses_per_frame = 19
        marked_values = pyrapt._get_marked_firstpass_results(candidates, params)
        self.assertEqual(3, len(marked_values))
        self.assertEqual((9, 0.6), marked_values[1])

    def test_get_makred_firstpass_results_above_max(self):
        candidates = ([0.7, 0.2, 0.6, 0.8, 0.9, 0.5], 1.0)
        params = (raptparams.Raptparams(), nccfparams.Nccfparams())
        params[1].shortest_lag_per_frame = 7
        params[0].min_acceptable_peak_val = 0.5
        params[0].max_hypotheses_per_frame = 5
        marked_values = pyrapt._get_marked_firstpass_results(candidates, params)
        self.assertEqual(4, len(marked_values))
        self.assertEqual((7, 0.7), marked_values[0])
        self.assertEqual((11, 0.9), marked_values[3])
        self.assertEqual((10, 0.8), marked_values[2])

    # TODO: have variable return values for mocks depending on inputs
    # TODO: verify inputs came in as expected:
    @patch('pyrapt.pyrapt._get_nccf_denominator_val')
    def test_get_correlation(self, mock_denominator):
        audio = (10, numpy.array([0, 1, 2, 3, 4, 5]))
        params = (raptparams.Raptparams(), nccfparams.Nccfparams())
        params[1].samples_correlated_per_lag = 5
        mock_denominator.return_value = 2.0
        with patch('pyrapt.pyrapt._get_sample') as mock_sample:
            mock_sample.return_value = 4.0
            correlation = pyrapt._get_correlation(audio, 0, 0, params)
            self.assertEqual(40.0, correlation)
            # Now try with additive constant added in denominator
            # (only added for 2nd pass NCCF calc)
            params[0].additive_constant = 12
            correlation = pyrapt._get_correlation(audio, 0, 0, params, False)
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
