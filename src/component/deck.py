"""
    This file has been mostly provided by Jonathan Vitale.
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""

import random

from component.card.action_card import ActionCard
from component.card.path_card import PathCard


class Deck:
    def __init__(self):
        self._deck = []
        # Create and shuffle the initial deck of cards
        self._initialise_deck()
        self.shuffle()
    
    def _initialise_deck(self):
        """
        Initialise the deck by adding cards to it.
        """
        # Add vertical tunnels
        for _ in range(4):
            self._deck.append(PathCard.vertical_tunnel())

        # Add vertical junctions
        for _ in range(5):
            self._deck.append(PathCard.vertical_junction())

        # Add cross roads
        for _ in range(5):
            self._deck.append(PathCard.cross_road())

        # Add horizontal junctions
        for _ in range(5):
            self._deck.append(PathCard.horizontal_junction())

        # Add horizontal tunnels
        for _ in range(3):
            self._deck.append(PathCard.horizontal_tunnel())

        # Add turns
        for _ in range(4):
            self._deck.append(PathCard.turn())

        # Add reversed turns
        for _ in range(5):
            self._deck.append(PathCard.reversed_turn())

        # Add various dead end configurations
        self._deck.append(PathCard.dead_end(['south']))
        self._deck.append(PathCard.dead_end(['north', 'south']))
        self._deck.append(PathCard.dead_end(['north', 'east', 'south']))
        self._deck.append(PathCard.dead_end(['north', 'east', 'south', 'west']))
        self._deck.append(PathCard.dead_end(['west', 'north', 'east']))
        self._deck.append(PathCard.dead_end(['west', 'east']))
        self._deck.append(PathCard.dead_end(['south', 'east']))
        self._deck.append(PathCard.dead_end(['south', 'west']))
        self._deck.append(PathCard.dead_end(['west']))

        # Add map action cards
        for _ in range(6):
            self._deck.append(ActionCard('map'))

        # Add sabotage action cards
        for _ in range(9):
            self._deck.append(ActionCard('sabotage'))

        # Add mend action cards
        for _ in range(9):
            self._deck.append(ActionCard('mend'))

        # Add dynamite action cards
        for _ in range(3):
            self._deck.append(ActionCard('dynamite'))

    def shuffle(self):
        """
        Shuffle the deck.
        """
        random.shuffle(self._deck)

    def draw(self):
        """
        Draw a card from the deck.\n
        Returns:
            Card: The card drawn from the deck.
        """
        assert self.cards_remaining() > 0, "There are no more cards in the deck"
        return self._deck.pop()
    
    def cards_remaining(self):
        """
        Get the number of cards remaining in the deck.\n
        Returns:
            int: The number of cards remaining in the deck.
        """
        return len(self._deck)
