"""
Unit tests for static util methods
"""
from unittest import TestCase

from pyrapt import pyrapt


class TestUtilityMethods(TestCase):

    def test_basic_downsampling_calc(self):
        assert pyrapt.calculate_downsampling_rate(48000, 500) == 2000

    def test_divide_by_zero_throws_value_error(self):
        with self.assertRaises(ValueError):
            pyrapt.calculate_downsampling_rate(500, 500)
