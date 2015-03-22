"""
This module defines the Pyrapt class, which encapsulates an implementation of 
David Talkin's Robust Algorithm for Pitch Tracking (RAPT).
"""

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

