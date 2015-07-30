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
        raptparam = (44100, [2.0] * 73000)
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
                mock_best.assert_called_with(ANY, ANY, [], 100, raptparam)

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

    @patch('pyrapt.pyrapt._get_delta_cost')
    def test_get_best_cost(self, mock_delta):
        mock_delta.return_value = 25
        candidate = (172, 0.542)
        params = raptparams.Raptparams()
        params.original_audio = (44100, [2.0] * 73000)
        cost = pyrapt._get_best_cost(candidate, 25, [], 100, params)
        self.assertEqual(50, cost)

    def test_get_delta_cost(self):
        cand1 = (172, 0.542)
        cand2 = (0, 0.0)
        prev_cand1 = (10, (215, 0.211))
        prev_cand2 = (10, (0, 0.0))
        params = raptparams.Raptparams()
        with patch('pyrapt.pyrapt._get_unvoiced_to_unvoiced_cost') as mok_cost1:
            mok_cost1.return_value = 5
            cost = pyrapt._get_delta_cost(cand2, prev_cand2, 25, params)
            self.assertEquals(5, cost)
            mok_cost1.assert_called_once_with(prev_cand2)
        with patch('pyrapt.pyrapt._get_voiced_to_unvoiced_cost') as mok_cost2:
            mok_cost2.return_value = 10
            cost = pyrapt._get_delta_cost(cand2, prev_cand1, 25, params)
            self.assertEquals(10, cost)
            mok_cost2.assert_called_once_with(cand2, prev_cand1, 25, params)
        with patch('pyrapt.pyrapt._get_unvoiced_to_voiced_cost') as mok_cost3:
            mok_cost3.return_value = 15
            cost = pyrapt._get_delta_cost(cand1, prev_cand2, 25, params)
            self.assertEquals(15, cost)
            mok_cost3.assert_called_once_with(cand1, prev_cand2, 25, params)
        with patch('pyrapt.pyrapt._get_voiced_to_voiced_cost') as mok_cost4:
            mok_cost4.return_value = 25
            cost = pyrapt._get_delta_cost(cand1, prev_cand1, 25, params)
            self.assertEquals(25, cost)
            mok_cost4.assert_called_once_with(cand1, prev_cand1, params)

    def test_is_unvoiced(self):
        voiced_cand = (172, 0.542)
        unvoiced_cand = (0, 0.0)
        partial_cand1 = (0, 0.672)
        partial_cand2 = (215, 0.0)
        self.assertTrue(pyrapt._is_unvoiced(unvoiced_cand))
        self.assertFalse(pyrapt._is_unvoiced(voiced_cand))
        self.assertFalse(pyrapt._is_unvoiced(partial_cand1))
        self.assertFalse(pyrapt._is_unvoiced(partial_cand2))

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

    @patch('pyrapt.pyrapt._get_rms_ratio')
    def test_voiced_to_unvoiced(self, mock_rms):
        mock_rms.return_value = 2.0
        candidate = (709, 0.733)
        prev_entry = (0.373, (650, 0.841))
        params = raptparams.Raptparams()
        params.transition_cost = 10.0
        params.amp_mod_transition_cost = 4.0
        cost = pyrapt._get_voiced_to_unvoiced_cost(candidate, prev_entry,
                                                   100, params)
        mock_rms.assert_called_once_with(100, params)
        self.assertEqual(18.373, cost)

    @patch('pyrapt.pyrapt._get_rms_ratio')
    def test_unvoiced_to_voiced(self, mock_rms):
        mock_rms.return_value = 2.0
        candidate = (709, 0.733)
        prev_entry = (0.373, (650, 0.841))
        params = raptparams.Raptparams()
        params.transition_cost = 10.0
        params.amp_mod_transition_cost = 4.0
        cost = pyrapt._get_unvoiced_to_voiced_cost(candidate, prev_entry,
                                                   100, params)
        mock_rms.assert_called_once_with(100, params)
        self.assertEqual(12.373, cost)

    # def test_spec_stationarity(self):
    #    result = pyrapt._get_spec_stationarity()
    #    self.assertAlmostEqual(1.0, result)

    def test_rms_ratio(self):
        # TODO: mock hanning window vals
        # start with basic test - if samples are all the same the frames will
        # match exactly and rms ratio will just be 1
        params = raptparams.Raptparams()
        params.original_audio = (2000, [2.0] * 73000)
        params.samples_per_frame = 5
        result = pyrapt._get_rms_ratio(100, params)
        self.assertEqual(1.0, result)
        # now test one where amp is increasing (rms ratio should be > 1)
        increasing_audio = [2.0] * 73000
        increasing_audio[540:600] = [4.0] * 60
        params.original_audio = (2000, increasing_audio)
        result = pyrapt._get_rms_ratio(100, params)
        self.assertGreater(result, 1.0)
        # now test where amp is decreasing (rms ratio should be btwn 0 and 1)
        decreasing_audio = [2.0] * 73000
        decreasing_audio[540:600] = [1.0] * 60
        params.original_audio = (2000, decreasing_audio)
        result = pyrapt._get_rms_ratio(100, params)
        self.assertGreater(result, 0.0)
        self.assertLess(result, 1.0)
