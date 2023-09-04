"""
    This file has been mostly provided by Jonathan Vitale.
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""

from src.component.card.card import Card
from src.exception.invalid_tunnel import InvalidTunnel

# Type of Path cards
PATH_CARD_TYPES = [
    'cross-road',
    'vertical-tunnel',
    'horizontal-tunnel',
    'vertical-junction',
    'horizontal-junction',
    'turn',
    'reversed-turn',
    'dead-end-south',
    'dead-end-north-south',
    'dead-end-north-east-south',
    'dead-end-north-east-south-west',
    'dead-end-west-north-east',
    'dead-end-west-east',
    'dead-end-south-east',
    'dead-end-south-west',
    'dead-end-west'
]


class PathCard(Card):

    def __init__(self, tunnels, path_type, special_card=None):
        """
        Initialise a PathCard instance.\n
        Args:
            tunnels (list): A list of tunnel tuples specifying the card's tunnels.
            path_type (str): The type of path card.
            special_card (str): The special type of card (None, 'start', 'goal', 'gold').
        """
        assert isinstance(tunnels, list), "The parameter tunnels must be a list of tuples"
        assert special_card in ['start', 'goal', 'gold',
                                None], "The parameter special_card must be either None, start, goal or gold"
        assert path_type in PATH_CARD_TYPES, "The parameter type must be a valid path card type"

        for tunnel in tunnels:
            if not self._is_valid_tunnel(tunnel):
                raise InvalidTunnel("The tunnel '{0}' is an invalid one for this card.".format(tunnel))

        self._path_type = path_type
        self._special_card = special_card
        self._revealed = True
        self._is_turned = False
        if special_card:
            # special cards are all cross roads
            cross_road = PathCard.cross_road()
            self._tunnels = cross_road.get_tunnels()
            if special_card in ['goal', 'gold']:
                self._revealed = False
            if special_card == 'gold':
                self._path_type = special_card
            if special_card == 'start':
                self._path_type = special_card
        else:
            self._tunnels = tunnels

    def copy(self):
        """
        Create a copy of the PathCard object.
        """
        copied_path_card = PathCard(
            self.get_tunnels(),
            self._path_type,
            self._special_card
        )
        copied_path_card._revealed = self._revealed
        copied_path_card._is_turned = self._is_turned
        return copied_path_card

    @staticmethod
    def cross_road(special_card=None):
        """
        Create a cross road PathCard.\n
        Args:
            special_card (str): The special type of card (None, 'start', 'goal', 'gold').
        Returns:
            PathCard: A cross road PathCard instance.
        """
        return PathCard(
            [
                ('north', 'south'),
                ('north', 'east'),
                ('north', 'west'),
                ('south', 'east'),
                ('south', 'west'),
                ('east', 'west')
            ],
            path_type='cross-road',
            special_card=special_card
        )

    @staticmethod
    def vertical_tunnel():
        """
        Create a vertical tunnel PathCard.\n
        """
        return PathCard(
            [
                ('north', 'south')
            ],
            path_type='vertical-tunnel'
        )

    @staticmethod
    def horizontal_tunnel():
        """
        Create a horizontal tunnel PathCard.\n
        """
        return PathCard(
            [
                ('east', 'west')
            ],
            path_type='horizontal-tunnel'
        )

    @staticmethod
    def vertical_junction():
        """
        Create a vertical junction PathCard.\n
        """
        return PathCard(
            [
                ('north', 'south'),
                ('north', 'east'),
                ('south', 'east')
            ],
            path_type='vertical-junction'
        )

    @staticmethod
    def horizontal_junction():
        """
        Create a horizontal junction PathCard.\n
        """
        return PathCard(
            [
                ('east', 'north'),
                ('west', 'north'),
                ('east', 'west')
            ],
            path_type='horizontal-junction'
        )

    @staticmethod
    def turn():
        """
        Create a turn PathCard.\n
        """
        return PathCard(
            [
                ('south', 'east')
            ],
            path_type='turn'
        )

    @staticmethod
    def reversed_turn():
        """
        Create a reversed turn PathCard.\n
        """
        return PathCard(
            [
                ('south', 'west')
            ],
            path_type='reversed-turn'
        )

    @staticmethod
    def dead_end(directions):
        """
        Create a dead-end PathCard with specified blocked directions.\n
        Args:
            directions (list): A list of directions to be blocked in the dead-end.
        Returns:
            PathCard: A dead-end PathCard instance with blocked directions.
        """
        tunnels = []
        for direction in directions:
            tunnels.append((direction, None))
        path_type = f"dead-end-{'-'.join(directions)}"
        return PathCard(tunnels, path_type=path_type)

    def get_path_type(self):
        """
        Get the type of the PathCard.\n
        Returns:
            str: The type of the PathCard.
        """
        return self._path_type

    def get_image_type(self):
        """
         Get the image type of the PathCard.\n
         Returns:
             str: The image type of the PathCard.
         """
        if self.is_special_card() and not self.is_revealed():
            return 'hidden'
        return self.get_path_type()

    @staticmethod
    def _is_valid_tunnel(tunnel):
        """
        Check if a given tunnel is a valid configuration for the card.\n
        Args:
            tunnel (tuple): A tuple representing the card's tunnel configuration.
        Returns:
            bool: True if the tunnel is valid, False otherwise.
        """
        if not isinstance(tunnel, tuple):
            return False
        if len(tunnel) != 2:
            return False
        for direction in tunnel:
            if direction not in ['north', 'east', 'south', 'west', None]:
                return False
        if tunnel[0] is None:
            return False
        if tunnel[0] is None and tunnel[1] is None:
            return False
        if tunnel[0] == tunnel[1]:
            return False

        return True

    def is_special_card(self):
        """
        Check if the card is a special card (start, goal, gold).\n
        Returns:
            bool: True if the card is special, False otherwise.
        """
        return self._special_card is not None

    def is_gold(self):
        """
        Check if the card is a gold card.\n
        Returns:
            bool: True if the card is a gold card, False otherwise.
        """
        return self._special_card == 'gold'

    def is_revealed(self):
        """
        Check if the card is revealed (visible).\n
        Returns:
            bool: True if the card is revealed, False otherwise.
        """
        return self._revealed

    def reveal_card(self):
        """
        Mark the card as revealed (visible).
        """
        self._revealed = True

    def turn_card(self):
        """
        Rotate the card 180 degrees, changing its tunnel configuration.
        """
        tunnels = []
        opposite = {
            'north': 'south',
            'east': 'west',
            'west': 'east',
            'south': 'north',
        }
        for tunnel in self._tunnels:
            new_tunnel = (
                opposite[tunnel[0]] if tunnel[0] is not None else None,
                opposite[tunnel[1]] if tunnel[1] is not None else None
            )
            tunnels.append(new_tunnel)

        self._tunnels = tunnels
        self._is_turned = not self._is_turned

    def is_card_turned(self):
        """
        Check if the card is turned (rotated 180 degrees).\n
        Returns:
            bool: True if the card is turned, False otherwise.
        """
        return self._is_turned

    def get_tunnels(self):
        """
        Get a copy of the card's tunnel configuration.
        Returns:
            list: A list of tuples representing the card's tunnel configuration.
        """
        return self._tunnels.copy()

    def get_type(self):
        """
        Get the path type associated with the card.\n
        Returns:
            str: The path type associated with the card.
        """
        return self._path_type
