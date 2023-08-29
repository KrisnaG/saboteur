"""
    This file has been mostly provided by Jonathan Vitale.
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""


class Card:
    pass


class ActionCard(Card):

    def __init__(self, action):
        assert action in ['map', 'sabotage', 'mend',
                          'dynamite'], "The parameter action must be either map, sabotage, mend or dynamite"

        self._action = action

    def get_action(self):
        return self._action


class InvalidTunnel(Exception):
    pass


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
        if special_card:
            # special cards are all cross roads
            cross_road = PathCard.cross_road()
            self._tunnels = cross_road.get_tunnels()
            if special_card in ['goal', 'gold']:
                self._revealed = False
            if special_card == 'gold':
                self._path_type = 'gold'
        else:
            self._tunnels = tunnels

    @staticmethod
    def cross_road(special_card=None):
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
        return PathCard(
            [
                ('north', 'south')
            ],
            path_type='vertical-tunnel'
        )

    @staticmethod
    def horizontal_tunnel():
        return PathCard(
            [
                ('east', 'west')
            ],
            path_type='horizontal-tunnel'
        )

    @staticmethod
    def vertical_junction():
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
        return PathCard(
            [
                ('south', 'east')
            ],
            path_type='turn'
        )

    @staticmethod
    def reversed_turn():
        return PathCard(
            [
                ('south', 'west')
            ],
            path_type='reversed-turn'
        )

    @staticmethod
    def dead_end(directions):
        tunnels = []
        for direction in directions:
            tunnels.append((direction, None))
        path_type = f"dead-end-{'-'.join(directions)}"
        return PathCard(tunnels, path_type=path_type)

    def get_path_type(self):
        return self._path_type

    def get_image_type(self):
        if self.is_special_card() and not self.is_revealed():
            return 'hidden'
        return self.get_path_type()

    def _is_valid_tunnel(self, tunnel):
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
        return self._special_card is not None

    def is_gold(self):
        return self._special_card == 'gold'

    def is_revealed(self):
        return self._revealed

    def reveal_card(self):
        self._revealed = True

    def turn_card(self):
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

    def get_tunnels(self):
        return self._tunnels.copy()

    def __str__(self):
        card_rep = ['   ', '   ', '   ']
        if self._revealed:
            for tunnel in self._tunnels:
                directions = [(tunnel[0], tunnel[1]), (tunnel[1], tunnel[0])]
                for direction in directions:
                    tunnel_from = direction[0]
                    tunnel_to = direction[1]
                    if tunnel_from == 'north':
                        card_rep[0] = card_rep[0][:1] + '|' + card_rep[0][2:]
                        if tunnel_to is not None:
                            card_rep[1] = card_rep[1][:1] + '┼' + card_rep[1][2:]
                    elif tunnel_from == 'south':
                        card_rep[2] = card_rep[2][:1] + '|' + card_rep[2][2:]
                        if tunnel_to is not None:
                            card_rep[1] = card_rep[1][:1] + '┼' + card_rep[1][2:]
                    elif tunnel_from == 'east':
                        card_rep[1] = card_rep[1][:2] + '—'
                        if tunnel_to is not None:
                            card_rep[1] = card_rep[1][:1] + '┼' + card_rep[1][2:]
                    elif tunnel_from == 'west':
                        card_rep[1] = '—' + card_rep[1][1:]
                        if tunnel_to is not None:
                            card_rep[1] = card_rep[1][:1] + '┼' + card_rep[1][2:]
        else:
            return '   \n ? \n   '
        return '\n'.join(card_rep)
