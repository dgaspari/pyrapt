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
