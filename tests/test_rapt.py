"""
Unit tests for main methods used by rapt
"""
from unittest import TestCase
from mock import patch

import numpy

from pyrapt import pyrapt


class TestMainRaptMethods(TestCase):

    @patch('pyrapt.pyrapt._get_audio_data')
    def test_rapt_control_flow(self, mock_getaudio):
        mock_getaudio.return_value = 44100, numpy.full(73641, 5.0)
        x, y = pyrapt.rapt('test.wav')
        mock_getaudio.called_once_with('test.wav')
        self.assertTrue(y < 1)
