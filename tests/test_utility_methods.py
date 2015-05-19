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
            pyrapt._get_audio_data('')

    @patch('scipy.io.wavfile.read')
    def test_read_data_simple(self, mock_wavfile_read):
        mock_wavfile_read.return_value = 100, numpy.full(5, 1)
        sample_rate, audio_sample = pyrapt._get_audio_data('test.wav')
        self.assertEqual(100, sample_rate)
        self.assertEqual(5, audio_sample.shape[0])
        self.assertEqual(1, audio_sample[0])

    @patch('scipy.io.wavfile.read')
    def test_read_data_with_mono_conversion(self, mock_wavfile_read):
        mock_sample = numpy.array([[1, -1], [2, 1], [3, 5]])
        mock_wavfile_read.return_value = 200, mock_sample
        sample_rate, audio_sample = pyrapt._get_audio_data('test.wav')
        self.assertTrue(numpy.array_equal(numpy.array([0, 1, 4]), audio_sample))
        self.assertTrue(200, sample_rate)

    def test_nccf_return_dimensions(self):
        sample_rate = 1000
        audio_data = numpy.zeros(1000)
        candidates = pyrapt._run_nccf(audio_data, sample_rate)
        self.assertEqual((100, 18), candidates.shape)

    def test_get_signal(self):
        # sample_rate = 1000
        audio_data = numpy.ones(1000)
        audio_data2 = numpy.zeros(1000)
        signal = pyrapt._get_samples_to_correlate(audio_data, 0, 10, 8, 20)
        self.assertEqual(1.0, signal)
        signal = pyrapt._get_samples_to_correlate(audio_data2, 0, 10, 8, 20)
        self.assertEqual(0, 0, signal)
