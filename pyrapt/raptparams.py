"""
Simple object that stores parameters to the RAPT processing logic.
"""


class Raptparams:
    """
    Simple object that stores parametrs for use in RAPT equations
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
