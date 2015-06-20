"""
Unit tests for methods used during NCCF calculations
"""
from unittest import TestCase
from mock import patch

import numpy

from pyrapt import pyrapt
from pyrapt import raptparams
from pyrapt import nccfparams


class TestNccfMethods(TestCase):

    @patch('pyrapt.pyrapt._get_correlation')
    def test_nccf_return_dimensions(self, mock_get_correlation):
        mock_get_correlation.return_value = 0.0
        # TODO: This is with default params. Do it with passed in ones as well
        sample_rate = 2004
        audio_data = numpy.full(3346, 5.0)
        params = raptparams.Raptparams()
        candidates, max_corr = pyrapt._first_pass_nccf((sample_rate,
                                                        audio_data), params)
        self.assertEqual((166, 35), candidates.shape)

    # TODO: test nccf param builder method

    # TODO: have variable return values for mocks depending on inputs
    # TODO: verify inputs came in as expected:
    @patch('pyrapt.pyrapt._get_nccf_denominator_val')
    def test_get_correlation(self, mock_denominator):
        audio = (10, numpy.array([0, 1, 2, 3, 4, 5]))
        params = nccfparams.Nccfparams()
        params.samples_correlated_per_lag = 5
        mock_denominator.return_value = 2.0
        with patch('pyrapt.pyrapt._get_sample') as mock_sample:
            mock_sample.return_value = 4.0
            correlation = pyrapt._get_correlation(audio, 0, 0, params)
            self.assertEqual(20.0, correlation)

    def test_get_sample(self):
        param = nccfparams.Nccfparams()
        param.samples_correlated_per_lag = 5
        param.samples_per_frame = 1
        audio_data = (10, numpy.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
        sample = pyrapt._get_sample(audio_data, 1, 5, param)
        self.assertEqual(3.0, sample)

    @patch('pyrapt.pyrapt._get_sample')
    def test_denominator(self, mock_get_signal):
        audio_data = (100, numpy.ones(1000))
        param = nccfparams.Nccfparams()
        param.samples_correlated_per_lag = 4
        mock_get_signal.return_value = 5.0
        returned = pyrapt._get_nccf_denominator_val(audio_data, 0, 1, param)
        self.assertEqual(100.0, returned)
        param.samples_correlated_per_lag = 3
        mock_get_signal.return_value = 2.0
        returned = pyrapt._get_nccf_denominator_val(audio_data, 0, 4, param)
        self.assertEqual(12.0, returned)
