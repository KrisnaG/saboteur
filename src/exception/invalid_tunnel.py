"""
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""


class InvalidTunnel(Exception):
    def __init__(self, message):
        super().__init__(message)
