"""
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""

from une_ai.models import Agent, GridMap

import src.constant.game_constants as gc
from src.component.card.card import Card
from src.component.card.path_card import PATH_CARD_TYPES
from src.component.deck import Deck
from src.component.game_board import GameBoard


class SaboteurPlayer(Agent):

    def __init__(self, agent_name, agent_program):
        super().__init__(agent_name, agent_program)

    def add_all_sensors(self):
        """
        Adds all the required sensors.
        Sensors: Game Board, Turn, Deck, Revealed Special Cards, Player, Type, Hand, Sabotage, and Seen.
        """
        # Game specific sensors

        # Game Board sensor
        self.add_sensor(
            sensor_name='game-board-sensor',
            initial_value=GameBoard(),
            validation_function=lambda game_board:
                isinstance(game_board.get_board(), GridMap) and
                all(
                    isinstance(cell, (Card, type(None))) for row in game_board.get_board_map() for cell in row)
        )

        # Turn Sensor
        self.add_sensor(
            sensor_name='turn-taking-indicator',
            initial_value='P0',
            validation_function=lambda turn:
                isinstance(turn, str) and
                turn in [f'P{i}' for i in range(gc.NUMBER_OF_PLAYERS)]
        )

        # Deck Sensor
        self.add_sensor(
            sensor_name='deck-sensor',
            initial_value=Deck(),
            validation_function=lambda deck:
                isinstance(deck, object)
        )

        # Revealed Special Card Sensor
        self.add_sensor(
            sensor_name='revealed-sensor',
            initial_value=[],
            validation_function=lambda cards:
                isinstance(cards, list) and
                all(isinstance(card, (Card, type(None))) for card in cards)
        )

        # Player specific sensors

        # Player sensor
        self.add_sensor(
            sensor_name='player-sensor',
            initial_value=None,
            validation_function=lambda player:
                isinstance(player, (dict, type(None)))
        )

        # Player Type sensor
        self.add_sensor(
            sensor_name='player-type-sensor',
            initial_value='gold-miner',
            validation_function=lambda player_type:
                isinstance(player_type, str) and
                player_type in ['gold-miner', 'saboteur']
        )

        # Hand sensor
        self.add_sensor(
            sensor_name='hand-sensor',
            initial_value=[],
            validation_function=lambda hand:
                isinstance(hand, list) and
                all(isinstance(card, (Card, type(None))) for card in hand)
        )

        # Sabotaged sensor
        self.add_sensor(
            sensor_name='sabotaged-sensor',
            initial_value=[],
            validation_function=lambda sabotage:
                isinstance(sabotage, list) and
                all(isinstance(card, str) for card in sabotage)
        )

        # Seen Sensor (from using Map card)
        self.add_sensor(
            sensor_name='seen-sensor',
            initial_value=[],
            validation_function=lambda cards:
                isinstance(cards, list) and
                all(isinstance(card, tuple) for card in cards)
        )

    def add_all_actuators(self):
        """
        Adds all the required actuators.
        Actuators: Play card
        """
        # Play card (action, coordinate/player/None, type/None)
        self.add_actuator(
            actuator_name='play-card',
            initial_value=('pass', None, None),
            validation_function=lambda action:
                isinstance(action, tuple) and
                len(action) == 3 and
                action[0] in ['mend', 'path', 'turn', 'map', 'dynamite', 'sabotage', 'pass'] and
                (isinstance(action[1], tuple) or isinstance(action[1], str) or action[1] is None) and
                (isinstance(action[2], str) or action[2] is None)
        )

    def add_all_actions(self):
        """
        Adds all the required actions.
        Actions: Mend, Path, Turn, Dynamite, Map, Sabotage and Pass
        """
        for row in range(gc.BOARD_ROW_SIZE):
            for col in range(gc.BOARD_COL_SIZE):
                if (row, col) != gc.START_POSITION:
                    if (row, col) not in gc.GOAL_POSITIONS:
                        for path_type in PATH_CARD_TYPES:
                            # Path
                            self.add_action(
                                action_name=f'path-{row}-{col}-{path_type}',
                                action_function=lambda r=row, c=col, p=path_type: {'play-card': ('path', (r, c), p)}
                            )

                            # Turn
                            self.add_action(
                                action_name=f'turn-{row}-{col}-{path_type}',
                                action_function=lambda r=row, c=col, p=path_type: {'play-card': ('turn', (r, c), p)}
                            )

                        # Dynamite
                        self.add_action(
                            action_name=f'dynamite-{row}-{col}',
                            action_function=lambda r=row, c=col: {'play-card': ('dynamite', (r, c), None)}
                        )
                    else:
                        # Map
                        self.add_action(
                            action_name=f'map-{row}-{col}',
                            action_function=lambda r=row, c=col: {'play-card': ('map', (r, c), None)}
                        )

        # Sabotage
        for index in range(gc.NUMBER_OF_PLAYERS):
            player = f'P{index}'
            self.add_action(
                action_name=f'sabotage-{player}',
                action_function=lambda p=player: {'play-card': ('sabotage', p, None)}
            )
            # Mend
            self.add_action(
                action_name=f'mend-{player}',
                action_function=lambda p=player: {'play-card': ('mend', p, None)}
            )

        # Pass
        for card in ['mend', 'path', 'dynamite', 'map', 'sabotage']:
            if card == 'path':
                for path_type in PATH_CARD_TYPES:
                    self.add_action(
                        action_name=f'pass-{card}-{path_type}',
                        action_function=lambda p=path_type: {'play-card': ('pass', None, f'path-{p}')}
                    )
            else:
                self.add_action(
                    action_name=f'pass-{card}',
                    action_function=lambda c=card: {'play-card': ('pass', None, c)}
                )
