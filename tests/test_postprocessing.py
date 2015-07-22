"""
Unit tests for postprocessing dynamic programming steps used by rapt
"""
from unittest import TestCase
from mock import patch

from pyrapt import pyrapt
from pyrapt import raptparams


class TestPostProcessingMethods(TestCase):

    @patch('pyrapt.pyrapt._determine_state_per_frame')
    def test_get_freq_estimate(self, mock_determine_state):
        mock_determine_state.return_value = [75] * 166
        raptparam = raptparams.Raptparams()
        nccf_results = [[(172, 0.5423), (770, 0.6772)]] * 166
        results = pyrapt._get_freq_estimate(nccf_results, raptparam, 44100)
        mock_determine_state.assert_called_once_with(nccf_results, raptparam,
                                                     44100)
        self.assertEqual(166, len(results))

    @patch('pyrapt.pyrapt._process_candidates')
    def test_determine_state_per_frame(self, mock_process):
        mock_process.return_value = [(172, 0.5423)] * 166
        raptparam = raptparams.Raptparams()
        nccf_results = [[(172, 0.5423), (770, 0.6772)]] * 166
        candidates = pyrapt._determine_state_per_frame(nccf_results, raptparam,
                                                       44100)
        self.assertEqual(166, len(candidates))
        mock_process.assert_called_once_with(165, [], nccf_results, raptparam,
                                             44100)

    def test_process_candidates(self):
        raptparam = raptparams.Raptparams()
        nccf_results = [[(172, 0.5423), (770, 0.6772)]] * 166
        candidates = pyrapt._process_candidates(165, [], nccf_results,
                                                raptparam, 44100)
        self.assertEqual(166, len(candidates))

    def test_select_max_correlation(self):
        nccf_results_frame = [(172, 0.5423), (235, 0.682), (422, 0.51),
                              (533, 0.822), (0, 0.0)]
        max_cand = pyrapt._select_max_correlation_for_frame(nccf_results_frame)
        self.assertEqual(0.822, max_cand)

    def test_calculate_local_cost(self):
        # standard voiced hypothesis calc:
        raptparam = raptparams.Raptparams()
        raptparam.lag_weight = 0.4
        raptparam.minimum_allowed_freq = 50
        correlation_val = 0.5423
        lag_val = 172
        max_corr_for_frame = 0.682
        sample_rate = 44100
        cost = pyrapt._calculate_local_cost(correlation_val, lag_val,
                                            max_corr_for_frame, raptparam,
                                            sample_rate)
        self.assertEqual(0.5000018594104307, cost)
        # now test unvoiced hypothesis calc:
        raptparam.voicing_bias = 10.0
        lag_val = 0
        correlation_val = 0.0
        cost = pyrapt._calculate_local_cost(correlation_val, lag_val,
                                            max_corr_for_frame, raptparam,
                                            sample_rate)
        self.assertEqual(10.682, cost)
