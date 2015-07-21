"""
Unit tests for postprocessing dynamic programming steps used by rapt
"""
from unittest import TestCase
# from mock import patch

from pyrapt import pyrapt
from pyrapt import raptparams


class TestPostProcessingMethods(TestCase):

    def test_get_freq_estimate(self):
        raptparam = raptparams.Raptparams()
        nccf_results = [[(172, 0.5423), (770, 0.6772)]] * 166
        results = pyrapt._get_freq_estimate(nccf_results, raptparam)
        self.assertEqual(166, len(results))
