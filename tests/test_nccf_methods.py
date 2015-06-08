"""
Unit tests for methods used during NCCF calculations
"""
from unittest import TestCase
# from mock import patch

import numpy

from pyrapt import pyrapt


class TestNccfMethods(TestCase):

    def test_nccf_return_dimensions(self):
        # TODO: This is with default params. Do it with passed in ones as well
        sample_rate = 1000
        audio_data = numpy.zeros(1000)
        candidates, max_corr = pyrapt._first_pass_nccf(audio_data, sample_rate)
        self.assertEqual((99, 17), candidates.shape)

    def test_get_signal(self):
        # sample_rate = 1000
        audio_data = numpy.ones(1000)
        audio_data2 = numpy.zeros(1000)
        signal = pyrapt._get_sample(audio_data, 0, 0, 10, 8, 20)
        self.assertEqual(0.125, signal)
        signal = pyrapt._get_sample(audio_data2, 0, 0, 10, 8, 20)
        self.assertEqual(0, 0, signal)
        signal = pyrapt._get_sample(audio_data, 5, 0, 10, 8, 20)
        self.assertEqual(0.125, signal)
