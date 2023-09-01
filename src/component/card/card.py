"""
    This file has been mostly provided by Jonathan Vitale.
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""
from abc import abstractmethod


class Card:
    @abstractmethod
    def get_type(self):
        pass
