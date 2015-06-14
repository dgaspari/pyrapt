"""
Simple object that stores parameters for NCCF equations.
"""


class Nccfparams:
    """
    Simple object that stores parameters for use in NCCF equations
    """
    def __init__(self):
        # Value of "n" in NCCF equation:
        self.samples_correlated_per_lag = None

        # starting value for "k" in 1st-pass of NCCF equation
        self.shortest_lag_per_frame = None

        # Value of "K" in NCCF equation
        self.longest_lag_per_frame = None

        # Value of "z" in NCCF equation
        self.samples_per_frame = None

        # Value of "M-1" in NCCF equation
        self.max_frame_count = None
