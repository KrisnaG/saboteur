"""
    This file has been mostly provided by Jonathan Vitale.
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""

from une_ai.models import GridMap
import random

import src.constant.game_constants as gc
from src.component.card import PathCard


class GameBoard:

    def __init__(self):
        """
        Initialise the GameBoard with the initial configuration.
        """
        self._board = GridMap(gc.BOARD_ROW_SIZE, gc.BOARD_COL_SIZE, None)

        start_card = PathCard.cross_road(special_card='start')
        goal_cards = []
        gold_idx = random.choice([0, 1, 2])

        for i in range(3):
            if gold_idx == i:
                label = 'gold'
            else:
                label = 'goal'
            goal_cards.append(PathCard.cross_road(special_card=label))

        # Place the start card on the board
        self._board.set_item_value(gc.START_POSITION[0], gc.START_POSITION[1], start_card)

        # Place goal cards on the board at specified positions
        for i, goal in enumerate(goal_cards):
            self._board.set_item_value(gc.GOAL_POSITIONS[i][0], gc.GOAL_POSITIONS[i][1], goal)

    @staticmethod
    def is_on_board(x, y):
        """
        Static function. Check if the given coordinates (x, y) are within the bounds of the game board.\n
        Args:
            x (int): The x-coordinate to check.
            y (int): The y-coordinate to check.
        Returns:
            bool: True if the coordinates are within the board bounds, False otherwise.
        """
        return x >= 0 and x < gc.BOARD_ROW_SIZE and y >= 0 and y < gc.BOARD_COL_SIZE

    @staticmethod
    def opposite_direction(direction):
        """
        Static function. Get the opposite direction of the given direction.\n
        Args:
            direction (str): The input direction.
        Returns:
            str: The opposite direction.
        """
        if direction == 'north':
            return 'south'
        if direction == 'south':
            return 'north'
        if direction == 'east':
            return 'west'
        if direction == 'west':
            return 'east'

    @staticmethod
    def can_place_card(x, y, path_card, board):
        """
        Static function. Check if a path card can be placed at the specified coordinates on the board.\n
        Args:
            x (int): The x-coordinate.
            y (int): The y-coordinate.
            path_card (PathCard): The path card to be placed.
            board (GridMap): The game board.
        Returns:
            bool: True if the card can be placed, False otherwise.
        """
        return (GameBoard.is_on_board(x, y) and
                board.get_item_value(x, y) is None and
                GameBoard.can_reach_target((x, y), path_card, gc.START_POSITION, board))

    @staticmethod
    def can_reach_target(start_location, start_card, target_location, incoming_board):
        """
        Static function. Check if the target card is reachable from the start card.\n
        Args:
            start_location (tuple[int, int]): The starting location (x, y).
            start_card (Card): The start card being placed.
            target_location (tuple[int, int]): The target location (x, y).
            incoming_board (GridMap): The game board with cards.
        Returns:
            bool: True if the target is reachable from the start, False otherwise.
        """
        visited = set()
        queue = [start_location]
        board = incoming_board.copy()

        # Add the start card to the start location if it's not present
        if board.get_item_value(start_location[0], start_location[1]) is None:
            board.set_item_value(start_location[0], start_location[1], start_card)

        while queue:
            x, y = queue.pop(0)
            visited.add((x, y))

            # We've reached out target
            if (x, y) == target_location:
                return True

            neighbours = {
                'north': (x - 1, y),
                'south': (x + 1, y),
                'west': (x, y - 1),
                'east': (x, y + 1)
            }

            current_card_tunnels = board.get_item_value(x, y).get_tunnels()

            # Check each neighbouring card
            for direction, location in neighbours.items():
                nx, ny = location
                # 
                if (GameBoard.is_on_board(nx, ny) and
                        (nx, ny) not in visited and
                        board.get_item_value(nx, ny) is not None):

                    # Now check if the current card can get to the neighbouring card
                    neighbour_card_tunnels = board.get_item_value(nx, ny).get_tunnels()
                    if (any(direction in tunnel for tunnel in current_card_tunnels) and
                            any(GameBoard.opposite_direction(direction) in tunnel for tunnel in
                                neighbour_card_tunnels) and
                            any(GameBoard.opposite_direction(direction) in tunnel and None not in tunnel for tunnel in
                                neighbour_card_tunnels)):
                        # Append the valid neighbouring card
                        queue.append((nx, ny))

        return False

    def get_width(self):
        """
        Get the width of the game board.\n
        Returns:
            int: The width of the game board.
        """
        return self._board.get_width()

    def get_height(self):
        """
        Get the height of the game board.\n
        Returns:
            int: The height of the game board.
        """
        return self._board.get_height()

    def get_board_map(self):
        """
        Get the map representation of the game board.\n
        Returns:
            list[list[Card]]: The map representation of the game board.
        """
        return self._board.get_map()

    def get_board(self):
        """
        Get the underlying grid map representing the game board.\n
        Returns:
            GridMap: The underlying grid map representing the game board.
        """
        return self._board

    def add_path_card(self, x, y, path_card):
        """
        Add a path card to the game board at the specified coordinates.\n
        Args:
            x (int): The x-coordinate of the placement.
            y (int): The y-coordinate of the placement.
            path_card (PathCard): The path card to be added.
        Raises:
            AssertionError: On invalid placement.
        """
        assert isinstance(path_card, PathCard), "The parameter path_card must be an instance of the class PathCard"
        assert 0 <= x < 20, "The x coordinate must be 0 <= x < 20"
        assert 0 <= y < 20, "The y coordinate must be 0 <= y < 20"
        assert self._board.get_item_value(x, y) is None, \
            ("There is already another card on the board at coordinates ({0}, {1})".format(x, y))
        assert GameBoard.can_reach_target((x, y), path_card, gc.START_POSITION, self._board), \
            f"This is not a valid placement of card at ({x}, {y})"
        self._board.set_item_value(x, y, path_card)

    def can_remove_card(self, x, y):
        """
        Check if a path card can be removed at the specified coordinates.\n
        Args:
            x (int): The x-coordinate.
            y (int): The y-coordinate.
        Returns:
            bool: True if the card can be removed, False otherwise.
        """
        card = self._board.get_item_value(x, y)
        return (GameBoard.is_on_board(x, y) and
                card is not None and
                not card.is_special_card())

    def remove_path_card(self, x, y):
        """
        Remove a path card from the game board at the specified coordinates.\n
        Args:
            x (int): The x-coordinate of the card to be removed.
            y (int): The y-coordinate of the card to be removed.
        Raises:
            AssertionError: Invalid removal of card.
        """
        assert 0 <= x < 20, "The x coordinate must be 0 <= x < 20"
        assert 0 <= y < 20, "The y coordinate must be 0 <= y < 20"
        assert self._board.get_item_value(x, y) is not None and not self._board.get_item_value(x, y).is_special_card(), \
            ("There is no valid card to remove at coordinates ({0}, {1})".format(x, y))

        self._board.set_item_value(x, y, None)

    def __str__(self):
        """
        Generate a string representation of the game board.\n
        Returns:
            str: The string representation of the game board.
        """
        no_card = '   \n   \n   '
        board_map = self._board.get_map()
        board_str = ''
        for row in board_map:
            for i in range(3):
                for card in row:
                    if card is None:
                        board_str += no_card.split('\n')[i]
                    else:
                        board_str += str(card).split('\n')[i]
                board_str += '\n'

        return board_str
