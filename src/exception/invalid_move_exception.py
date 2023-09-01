"""
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""


class InvalidMoveException(Exception):
    def __init__(self, message):
        super().__init__(message)
