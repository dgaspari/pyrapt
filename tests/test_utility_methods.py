"""
Unit tests for utility methods
"""
from unittest import TestCase
# import numpy

from pyrapt import pyrapt


class TestUtilityMethods(TestCase):

    def test_null_input_error(self):
        with self.assertRaises(IOError):
            pyrapt.rapt('')
