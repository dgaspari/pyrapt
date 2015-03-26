"""
This module defines the Pyrapt class, which encapsulates an implementation of 
David Talkin's Robust Algorithm for Pitch Tracking (RAPT).
"""

from scipy import signal
from scipy.io import wavfile

class Pyrapt(object):
    """ 
    This class handles the processing of a speech audio sample and the output
    of an estimated pitch for each point in the sample.
    """

    @staticmethod
    def calculate_downsampling_rate(initial_sampling_rate, maximum_f0):
        """
        Determines downsampling rate to apply to the audio input passed for RAPT processing
        """
        #TODO: validate inputs, check for divide by 0
        aReturn = initial_sampling_rate / round( initial_sampling_rate / (4 * maximum_f0) )
        return aReturn

    @staticmethod
    def demo(wavfile_path):
        """
        Rough demo of the RAPT alg process - downsampling input audio, cross-correlation
        first pass on downsampled audio, then second pass on the original audio. Followed
        by the dynamic programming steps. The logic here will be refined in the rest of
        class.
        """
        #get audio input data using scipy.io wav reader:
        original_audio = wavfile.read(wavfile_path)
        downsampling_rate = Pyrapt.calculate_downsampling_rate(original_audio[0], 500) #2nd arg could be constant configurable - max Fzero
        #downsampled_audio = signal.resample(original_audio[1], int(downsampling_rate)) #decimate or resample options available here:
        downsampled_audio = signal.decimate(original_audio[1], int(downsampling_rate)) #TODO: need details on lowpass fir filter
        return downsampled_audio
