"""
Unit tests for main methods used by rapt
"""
from unittest import TestCase
from mock import patch

import numpy

from pyrapt import pyrapt


class TestMainRaptMethods(TestCase):

    @patch('pyrapt.pyrapt._get_audio_data')
    def test_rapt_control_flow(self, mock_audio):
        mock_audio.return_value = (44100, numpy.full(100, 3.0))
        with patch('pyrapt.pyrapt._get_downsampled_audio') as mock_downsample:
            mock_downsample.return_value = (2004, numpy.full(10, 2.0))
            with patch('pyrapt.pyrapt._run_nccf') as mock_get_nccf:
                mock_get_nccf.return_value = [([0.2] * 35, 0.3)] * 166
                with patch('pyrapt.pyrapt._get_freq_estimate') as mock_get_freq:
                    mock_get_freq.return_value = [75] * 166
                    results = pyrapt.rapt('test.wav')
                    self.assertEqual(166, len(results))
                    self.assertEqual(75, results[0])
