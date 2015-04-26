"""
Unit tests for utility methods
"""
from unittest import TestCase
import numpy

from pyrapt import pyrapt


class TestUtilityMethods(TestCase):

    def test_basic_downsampling_calc(self):
        assert pyrapt.calculate_downsampling_rate(48000, 500) == 2000

    def test_divide_by_zero_throws_value_error(self):
        with self.assertRaises(ValueError):
            pyrapt.calculate_downsampling_rate(500, 500)

    def test_nccf_first_pass_basic_example(self):
        empty_input = numpy.zeros(3600)
        results = pyrapt.nccf_first_pass(empty_input, 2000, 44100)
        assert results.shape == (180, 36)
