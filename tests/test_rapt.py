"""
Unit tests for main methods used by rapt
"""
from unittest import TestCase
from mock import patch

import numpy

from pyrapt import pyrapt


class TestMainRaptMethods(TestCase):

    @patch('pyrapt.pyrapt._get_audio_data')
    @patch('pyrapt.pyrapt._get_downsampled_audio')
    @patch('pyrapt.pyrapt._run_nccf')
    def test_rapt_control_flow(self, mock_audio, mock_downsample, mock_nccf):
        mock_audio.return_value = (44100, numpy.full(100, 3.0))
        with patch('pyrapt.pyrapt._get_downsampled_audio') as mock_downsample:
            mock_downsample.return_value = (2004, numpy.full(10, 2.0))
            with patch('pyrapt.pyrapt._run_nccf') as mock_get_nccf:
                mock_get_nccf.return_value = (numpy.zeros((10, 10)), 0.5)
                x, y = pyrapt.rapt('test.wav')
                self.assertEqual(y, 0.5)
