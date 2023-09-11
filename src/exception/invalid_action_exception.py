"""
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""


class InvalidActionException(Exception):
    """
    Exception specifying that an action is invalid.
    """
    def __init__(self, message):
        super().__init__(message)
