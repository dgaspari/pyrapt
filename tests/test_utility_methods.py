"""
Unit tests for utility methods
"""
from unittest import TestCase
import numpy

from pyrapt import pyrapt


class TestUtilityMethods(TestCase):

    def test_placeholder(self):
        empty_input = numpy.zeros(3600)
        results = pyrapt.run_nccf(empty_input, 44100)
        assert results.shape == (8, 794)
