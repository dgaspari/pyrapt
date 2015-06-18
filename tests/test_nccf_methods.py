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

    def test_nccf_return_dimensions(self):
        # TODO: This is with default params. Do it with passed in ones as well
        sample_rate = 2004
        audio_data = numpy.full(3346, 5.0)
        params = raptparams.Raptparams()
        candidates, max_corr = pyrapt._first_pass_nccf((sample_rate,
                                                        audio_data), params)
        self.assertEqual((166, 35), candidates.shape)

    def test_get_signal(self):
        param = nccfparams.Nccfparams()
        param.samples_correlated_per_lag = 8
        param.samples_per_frame = 10

        # sample_rate = 1000
        audio_data = (100, numpy.ones(1000))
        audio_data2 = (100, numpy.zeros(1000))
        signal = pyrapt._get_sample(audio_data, 0, 0, param)
        self.assertEqual(0.125, signal)
        signal = pyrapt._get_sample(audio_data2, 0, 0, param)
        self.assertEqual(0, 0, signal)
        signal = pyrapt._get_sample(audio_data, 5, 0, param)
        self.assertEqual(0.125, signal)

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
        returned = pyrapt._get_nccf_denominator_val(audio_data, 0, 0, param)
        self.assertEqual(75, returned)
