"""
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""


class InvalidMoveException(Exception):
    """
    Exception specifying that a move is invalid.
    """
    def __init__(self, message):
        super().__init__(message)
