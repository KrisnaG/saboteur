"""
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""


class InvalidTunnel(Exception):
    """
    Exception specifying that the tunnel is invalid.
    """
    def __init__(self, message):
        super().__init__(message)
