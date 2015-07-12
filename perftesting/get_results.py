import cProfile
import re
from pyrapt import pyrapt
cProfile.run('pyrapt.rapt("example.wav")', 'example_run_profile3')
