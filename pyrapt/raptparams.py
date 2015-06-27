"""
Simple object that stores parameters to the RAPT processing logic.
"""


class Raptparams:
    """
    Simple object that stores const parameters for use in RAPT equations
    """

    def __init__(self):
        # Value of "F0_max" in NCCF equation:
        self.maximum_allowed_freq = 500

        # Value of "F0_min" in NCCF equation:
        self.minimum_allowed_freq = 50

        # Value of "t" in NCCF equation:
        self.frame_step_size = 0.01

        # Value of "w" in NCCF equation:
        self.correlation_window_size = 0.0075

        # Value of "N_CANDS" in NCCF equation:
        self.max_hypotheses_per_frame = 20

        # Value of "CAND_TR" in NCCF equation:
        self.min_acceptable_peak_val = 0.3

        # Value of A_FACT" in NCCF equation:
        self.additive_constant = 10000
