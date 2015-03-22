""" 
Unit tests for static util methods
"""
from unittest import TestCase

from pyrapt import pyrapt

class TestUtilityMethods(TestCase):

    def test_downsampling_calc(self):
        assert pyrapt.Pyrapt.calculate_downsampling_rate(48000,500) == 2000



