"""
    This file has been mostly provided by Jonathan Vitale.
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""

from src.component.card.card import Card


class ActionCard(Card):

    def __init__(self, action):
        """
        Initialise an ActionCard with a specific action.\n
        Args:
            action (str): The action associated with the card ('map', 'sabotage', 'mend', 'dynamite').
        """
        assert action in ['map', 'sabotage', 'mend',
                          'dynamite'], "The parameter action must be either map, sabotage, mend or dynamite"
        self._action = action

    def get_action(self):
        """
        Get the action associated with the card.\n
        Returns:
            str: The action associated with the card ('map', 'sabotage', 'mend', 'dynamite').
        """
        return self._action
