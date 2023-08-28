"""
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""

from une_ai.models import Agent
import src.constant.game_constants as gc
from src.component.game_board import GameBoard
from src.component.card import Card, PATH_CARD_TYPES


class SaboteurPlayer(Agent):

    def __init__(self, agent_name, agent_program):
        super().__init__(agent_name, agent_program)

    def add_all_sensors(self):
        """
        Adds all the required sensors.
        Sensors:
        """
        # Game Board sensor
        self.add_sensor(
            sensor_name='game-board-sensor',
            initial_value=GameBoard(),
            validation_function=lambda game_board:
                isinstance(game_board, GameBoard) and
                all(
                    isinstance(cell, (Card, type(None))) for row in game_board.get_board_map() for cell in row)
        )

        # Turn Sensor

        # Revealed Special Card Sensor

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
        # Mend
        self.add_action(
            action_name='mend',
            action_function=lambda: {'play-card': ('mend', None, None)}
        )

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
            opponent = f'P{index}'
            self.add_action(
                action_name=f'sabotage-{opponent}',
                action_function=lambda opp=opponent: {'play-card': ('sabotage', opp, None)}
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
