"""
Unit tests for utility methods that read and process incoming audio data
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
        mock_wavfile_read.called_once_with('test.wav')
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

    def test_basic_downsampling_calc(self):
        assert pyrapt._calculate_downsampling_rate(48000, 500) == 2000

    def test_divide_by_zero_throws_value_error(self):
        with self.assertRaises(ValueError):
            pyrapt._calculate_downsampling_rate(500, 500)

    @patch('scipy.signal.resample')
    def test_basic_audio_downsampling(self, mock_signal_resample):
        mock_sample = numpy.array([1, 2, 3])
        mock_signal_resample.return_value = mock_sample
        input_array = numpy.array([1, 2, 3, 4, 5])
        x = pyrapt._downsample_audio(input_array, 100, 10)
        mock_signal_resample.assert_called_once_with(input_array, .5)
        self.assertTrue(numpy.array_equal(numpy.array([1, 2, 3]), x))

    @patch('scipy.signal.resample')
    def test_downsampling_bad_input_sample_rate(self, mock_signal_resample):
        mock_sample = numpy.array([1, 2, 3])
        mock_signal_resample.return_value = mock_sample
        input_array = numpy.array([1, 2, 3])
        with self.assertRaises(ValueError):
            pyrapt._downsample_audio(input_array, 0, 10)
