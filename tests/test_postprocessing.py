"""
Unit tests for postprocessing dynamic programming steps used by rapt
"""
from unittest import TestCase
from mock import patch
from mock import ANY

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
        # now try it when returned results contain unvoiced hypothesis
        mock_determine_state.return_value = [50, 0, 75]
        results = pyrapt._get_freq_estimate(nccf_results, raptparam, 44100)
        self.assertEqual(0.0, results[1])

    @patch('pyrapt.pyrapt._process_candidates')
    def test_determine_state_per_frame(self, mock_process):
        mock_process.return_value = [[(25, (172, 0.5423))]] * 166
        raptparam = raptparams.Raptparams()
        nccf_results = [[(172, 0.5423), (770, 0.6772)]] * 166
        candidates = pyrapt._determine_state_per_frame(nccf_results, raptparam,
                                                       44100)
        self.assertEqual(166, len(candidates))
        mock_process.assert_called_once_with(165, [], nccf_results, raptparam,
                                             44100)

    @patch('pyrapt.pyrapt._calculate_costs_per_frame')
    def test_process_candidates(self, mock_calc_frame):
        mock_calc_frame.return_value = [(25, (172, 0.542)), (55, (770, 0.672))]
        raptparam = raptparams.Raptparams()
        nccf_results = [[(172, 0.5423), (770, 0.6772)]] * 166
        candidates = pyrapt._process_candidates(165, [], nccf_results,
                                                raptparam, 44100)
        mock_calc_frame.assert_called_with(ANY, ANY, nccf_results, raptparam,
                                           44100)
        self.assertEqual(166, len(candidates))

    @patch('pyrapt.pyrapt._select_max_correlation_for_frame')
    def test_calculate_cost_per_frame(self, mock_max_for_frame):
        mock_max_for_frame.return_value = 0.6772
        raptparam = raptparams.Raptparams()
        nccf_results = [[(172, 0.5423), (770, 0.6772)]] * 166
        with patch('pyrapt.pyrapt._calculate_local_cost') as mock_local:
            with patch('pyrapt.pyrapt._get_best_cost') as mock_best:
                mock_local.return_value = 25
                mock_best.return_value = 75
                candidates = pyrapt._calculate_costs_per_frame(100, [],
                                                               nccf_results,
                                                               raptparam, 44100)
                self.assertEqual(2, len(candidates))
                mock_max_for_frame.assert_called_once_with([(172, 0.5423),
                                                            (770, 0.6772)])
                mock_local.assert_called_with(ANY, 0.6772, raptparam, 44100)
                mock_best.assert_called_with(ANY, ANY, [], raptparam, 44100)

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
        max_corr_for_frame = 0.682
        sample_rate = 44100
        cost = pyrapt._calculate_local_cost((172, 0.5423), max_corr_for_frame,
                                            raptparam, sample_rate)
        self.assertEqual(0.5000018594104307, cost)
        # now test unvoiced hypothesis calc:
        raptparam.voicing_bias = 10.0
        cost = pyrapt._calculate_local_cost((0, 0.0), max_corr_for_frame,
                                            raptparam, sample_rate)
        self.assertEqual(10.682, cost)

    def test_get_best_cost(self):
        candidate = (172, 0.542)
        params = raptparams.Raptparams()
        cost = pyrapt._get_best_cost(candidate, 25, [], params, 44100)
        self.assertEqual(25, cost)

    def test_voiced_to_voiced(self):
        candidate = (709, 0.733)
        prev_entry = (0.373, (650, 0.841))
        params = raptparams.Raptparams()
        cost = pyrapt._get_voiced_to_voiced_cost(candidate, prev_entry, params)
        self.assertEqual(0.39212528033835004, cost)

    def test_unvoiced_to_unvoiced(self):
        prev_entry = (0.373, (0, 0.0))
        cost = pyrapt._get_unvoiced_to_unvoiced_cost(prev_entry)
        self.assertEqual(0.373, cost)

    @patch('pyrapt.pyrapt._get_spec_stationarity')
    def test_voiced_to_unvoiced(self, mock_spec_stationarity):
        with patch('pyrapt.pyrapt._get_rms_ratio') as mock_rms:
            mock_spec_stationarity.return_value = 1.0
            mock_rms.return_value = 2.0
            candidate = (709, 0.733)
            prev_entry = (0.373, (650, 0.841))
            params = raptparams.Raptparams()
            params.transition_cost = 10.0
            params.spec_mod_transition_cost = 5.0
            params.amp_mod_transition_cost = 2.0
            cost = pyrapt._get_voiced_to_unvoiced_cost(candidate, prev_entry,
                                                       params)
            self.assertEqual(19.373, cost)

    @patch('pyrapt.pyrapt._get_spec_stationarity')
    def test_unvoiced_to_voiced(self, mock_spec_stationarity):
        with patch('pyrapt.pyrapt._get_rms_ratio') as mock_rms:
            mock_spec_stationarity.return_value = 1.0
            mock_rms.return_value = 2.0
            candidate = (709, 0.733)
            prev_entry = (0.373, (650, 0.841))
            params = raptparams.Raptparams()
            params.transition_cost = 10.0
            params.spec_mod_transition_cost = 5.0
            params.amp_mod_transition_cost = 4.0
            cost = pyrapt._get_unvoiced_to_voiced_cost(candidate, prev_entry,
                                                       params)
            self.assertEqual(17.373, cost)
