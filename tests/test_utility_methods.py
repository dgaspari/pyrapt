"""
Unit tests for utility methods that read and process incoming audio data
"""
from unittest import TestCase
from mock import patch

import numpy

from pyrapt import pyrapt
from pyrapt import raptparams


class TestUtilityMethods(TestCase):

    def test_empty_kwargs(self):
        params = pyrapt._setup_rapt_params(None)
        self.assertEqual(500, params.maximum_allowed_freq)
        self.assertEqual(50, params.minimum_allowed_freq)
        self.assertEqual(0.01, params.frame_step_size)
        self.assertEqual(0.0075, params.correlation_window_size)
        self.assertEqual(20, params.max_hypotheses_per_frame)
        self.assertEqual(0.3, params.min_acceptable_peak_val)
        self.assertEqual(10000, params.additive_constant)
        self.assertEqual(0.35, params.doubling_cost)
        self.assertEqual(0.0, params.voicing_bias)
        self.assertEqual(0.3, params.lag_weight)
        self.assertEqual(0.02, params.freq_weight)
        self.assertEqual(None, params.sample_rate_ratio)
        self.assertEqual(None, params.original_audio)
        self.assertEqual(None, params.samples_per_frame)

    def test_custom_kwargs(self):
        params = pyrapt._setup_rapt_params({'maximum_allowed_freq': 250,
                                            'minimum_allowed_freq': 100,
                                            'frame_step_size': 0.5,
                                            'correlation_window_size': 75,
                                            'max_hypotheses_per_frame': 5,
                                            'min_acceptable_peak_val': 1.5,
                                            'additive_constant': 100,
                                            'doubling_cost': 0.4})
        self.assertEqual(250, params.maximum_allowed_freq)
        self.assertEqual(100, params.minimum_allowed_freq)
        self.assertEqual(0.5, params.frame_step_size)
        self.assertEqual(75, params.correlation_window_size)
        self.assertEqual(5, params.max_hypotheses_per_frame)
        self.assertEqual(1.5, params.min_acceptable_peak_val)
        self.assertEqual(100, params.additive_constant)
        self.assertEqual(0.4, params.doubling_cost)
        self.assertEqual(None, params.sample_rate_ratio)

    def test_partial_custom_kwargs(self):
        params = pyrapt._setup_rapt_params({'correlation_window_size': 88})
        self.assertEqual(500, params.maximum_allowed_freq)
        self.assertEqual(50, params.minimum_allowed_freq)
        self.assertEqual(0.01, params.frame_step_size)
        self.assertEqual(88, params.correlation_window_size)
        self.assertEqual(10000, params.additive_constant)
        self.assertEqual(0.02, params.freq_weight)
        self.assertEqual(None, params.sample_rate_ratio)
        self.assertEqual(None, params.original_audio)

    @patch('numpy.hanning')
    def test_calculate_params(self, mock_hanning):
        params = raptparams.Raptparams()
        self.assertEqual(None, params.original_audio)
        self.assertEqual(None, params.samples_per_frame)
        mock_hanning.return_value = [1, 2, 3, 4, 5]
        audio = (44100, [5.0] * 7000)
        down_audio = (2000, [5.0] * 700)
        pyrapt._calculate_params(params, audio, down_audio)
        mock_hanning.assert_called_once_with(1323)
        self.assertEqual(22.05, params.sample_rate_ratio)
        self.assertEqual(audio, params.original_audio)
        self.assertEqual(441, params.samples_per_frame)
        self.assertEqual(1323, params.hanning_window_length)
        self.assertEqual([1, 2, 3, 4, 5], params.hanning_window_vals)
        self.assertEqual(882, params.rms_offset)

    def test_non_dict_input_kwrags(self):
        not_a_dict = 'foo'
        params = pyrapt._setup_rapt_params(not_a_dict)
        self.assertEqual(500, params.maximum_allowed_freq)
        self.assertEqual(0.01, params.frame_step_size)

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
        x = pyrapt._downsample_audio((100, input_array), 10)
        mock_signal_resample.assert_called_once_with(input_array, .5)
        self.assertTrue(numpy.array_equal(numpy.array([1, 2, 3]), x))

    @patch('scipy.signal.resample')
    def test_downsampling_bad_input_sample_rate(self, mock_signal_resample):
        mock_sample = numpy.array([1, 2, 3])
        mock_signal_resample.return_value = mock_sample
        input_array = numpy.array([1, 2, 3])
        with self.assertRaises(ValueError):
            pyrapt._downsample_audio((0, input_array), 10)
