"""
Unit tests for utility methods
"""
from unittest import TestCase
from mock import patch

import numpy

from pyrapt import pyrapt


class TestUtilityMethods(TestCase):

    def test_null_input_error(self):
        with self.assertRaises(IOError):
            pyrapt._get_sample_data('')

    @patch('scipy.io.wavfile.read')
    def test_read_data_simple(self, mock_wavfile_read):
        mock_wavfile_read.return_value = 100, numpy.full(5, 1)
        sample_rate, audio_sample = pyrapt._get_sample_data('test.wav')
        self.assertEqual(100, sample_rate)
        self.assertEqual(5, audio_sample.shape[0])
        self.assertEqual(1, audio_sample[0])

    @patch('scipy.io.wavfile.read')
    def test_read_data_with_mono_conversion(self, mock_wavfile_read):
        mock_wavfile_read.return_value = 100, numpy.empty([0])
        sample_rate, audio_sample = pyrapt._get_sample_data('test.wav')
        # TODO: verify conversion of 2-channel stereo data converted to mono
