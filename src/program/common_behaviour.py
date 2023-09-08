"""
Common Behaviour shared between the Gold Miner and Saboteur.

Author:
    Krisna Gusti (kgusti@myune.edu.au)
"""

import math
import random

from src.component.game_board import GameBoard
import src.constant.game_constants as gc


class CommonBehaviour:
    @staticmethod
    def behaviour(game_state, kb):
        pass

    @staticmethod
    def euclidean_distance(x1, x2, y1, y2):
        """
        Calculate the Euclidean distance between two points (x1, y1) and (x2, y2).\n
        Args:
            x1 (float): X-coordinate of the first point.
            x2 (float): X-coordinate of the second point.
            y1 (float): Y-coordinate of the first point.
            y2 (float): Y-coordinate of the second point.
        Returns:
            float: The Euclidean distance between the two points.
        """
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    @staticmethod
    def evaluate_state(game_board, aim, action):
        """
        Evaluate the payoff for placing a path card at a given action position based on its distance from the aim and
        the available tunnels facing the aim direction.\n
        Args:
            game_board (GameBoard): The game board containing information about the current state of the board.
            aim (tuple): The target coordinates (x, y) where the path card is intended to connect.
            action (str): The action representing the placement of a path card.
        Returns:
            float: The calculated payoff value for placing the path card at the specified position.
        """
        parts = action.split('-')
        x = int(parts[1])
        y = int(parts[2])
        payoff = 0

        # Calculate the Euclidean distance between the action position and the aim
        distance = CommonBehaviour.euclidean_distance(aim[0], x, aim[1], y)
        payoff += 10 / (1 + distance)

        # If the distance is 1 (adjacent position), add a bonus to the payoff
        if distance == 1:
            payoff += 2.0

        # Get the path card at the action position and its available tunnels
        card = game_board.get_board().get_item_value(x, y)
        tunnels = [item for sublist in card.get_tunnels() for item in sublist]

        # Define neighboring positions in cardinal directions
        neighbours = {
            'north': (x - 1, y),
            'south': (x + 1, y),
            'west': (x, y - 1),
            'east': (x, y + 1)
        }

        # Determine the direction from the action position to the aim
        direction = ""
        if x < aim[0]:
            direction = "south"
        elif x > aim[0]:
            direction = "north"
        elif y > aim[1]:
            direction = "east"
        elif y < aim[1]:
            direction = "west"

        # Evaluate the payoff based on available tunnels and direction
        for n_direction, location in neighbours.items():
            nx, ny = location
            if GameBoard.is_on_board(nx, ny):
                n_card = game_board.get_board().get_item_value(nx, ny)
                if n_card is None and n_direction in tunnels:
                    if direction == n_direction:
                        payoff += 1.2
                    elif GameBoard.opposite_direction(direction) == n_direction:
                        payoff -= 0.5
                    else:
                        payoff += 0.6

        return payoff

    @staticmethod
    def infer_gold(seen, revealed):
        """
        Infers the possible gold positions from what has been seen and revealed.
        Args:
            seen (list): A list of tuples containing positions and a bool indicating if the card at that position is seen.
            revealed (list): A list of positions where cards have been revealed.
        Returns:
            tuple: Goal positions that was inferred to be a gold card.
        """
        goal_positions = gc.GOAL_POSITIONS.copy()
        for item, _ in seen:
            if item in goal_positions:
                goal_positions.remove(item)
        for item in revealed:
            if item in goal_positions:
                goal_positions.remove(item)
        return goal_positions

    @staticmethod
    def find_goal_card_aim(seen, revealed, announcements, kb):
        """
        Determine the aim position for a goal card placement based on seen and revealed cards.\n
        Args:
            seen (list): A list of tuples containing positions and a bool indicating if the card at that position is seen.
            revealed (list): A list of positions where cards have been revealed.
            announcements (dict): Announcements made by other players.
            kb (dict): The knowledge base containing information about other players.
        Returns:
            tuple or None: The target position (aim) for placing a goal card, or None if no specific aim is determined.
        """
        aim = None

        # Aim for a card that has not been revealed
        for position in gc.GOAL_POSITIONS:
            if position not in revealed:
                aim = position
                break

        # Have we seen a gold card?
        gold_seen = [seen_item for seen_item in seen if seen_item[1]]
        if len(gold_seen) > 0:
            return gold_seen[0][0]

        # Can we infer where the gold is?
        inferred = CommonBehaviour.infer_gold(seen, revealed)
        if len(inferred) == 1:
            return inferred[0]

        # What have other players announced?
        for player, content in announcements.items():
            # Do we trust the player that made the announcement?
            if len(content) > 0 and kb[player] == 'gold-miner':
                for pos, result in content:
                    # gold seen for this position
                    if result:
                        return pos
                    # gold not seen for the position
                    elif pos == aim:
                        for position in gc.GOAL_POSITIONS:
                            if position not in revealed and position != pos:
                                aim = position

        return aim

    @staticmethod
    def sabotage_player(legal_actions, player, kb, opposition, thresh_hold):
        """
        Determine the appropriate sabotage action for the player based on their knowledge and suspicions.\n
        Args:
            legal_actions (list): List of legal actions available to the player.
            player (str): The player who wants to take a sabotage action.
            kb (dict): Knowledge base containing player roles (gold-miner or saboteur).
            opposition (string): The player type (gold-miner or saboteur).
            thresh_hold (float): Thresh hold to sabotage player (in the interval [0, 1))
        Returns:
            list or None: A list containing the sabotage action for the player, or None if no sabotage action is taken.
        """
        sabotage_actions = [action for action in legal_actions if action.startswith('sabotage')]
        random.shuffle(sabotage_actions)

        # Who can we sabotage?
        for action in sabotage_actions:
            other_player = action.split('-')[1]
            if other_player == player:
                continue
            # Do we suspect the player being the opposition?
            if kb[other_player] == opposition:
                # 'Roll a dice' to sabotage
                if random.random() < thresh_hold:
                    return [action]

        # If we don't suspect any saboteur players, don't take any sabotage actions
        return None

    @staticmethod
    def mend_player(legal_actions, player, sabotaged_players, kb, team_member):
        """
        Determine the appropriate mend action for the player based on their current state and knowledge.\n
        Args:
            legal_actions (list): List of legal actions available to the player.
            player (str): The player for whom mend actions are being considered.
            sabotaged_players (list): List of players who are sabotaged.
            kb (dict): Knowledge base containing player roles (gold-miner or saboteur).
            team_member (string): The player type (gold-miner or saboteur).
        Returns:
            list or None: A list containing the mend action for the player, or None if no mend action is taken.
        """
        mend_actions = [action for action in legal_actions if action.startswith('mend')]
        random.shuffle(mend_actions)

        # Is the current player sabotaged?
        if player in sabotaged_players:
            return [action for action in mend_actions if action.endswith(player)]

        # What other players are sabotaged?
        for other_player in sabotaged_players:
            # Do we trust the player that is sabotaged?
            if kb[other_player] == team_member:
                return [action for action in mend_actions if action.endswith(other_player)]

        # If we don't trust any sabotaged players, don't take any mend actions
        return None

    @staticmethod
    def map_for_gold(legal_actions, seen, revealed):
        """
        Find the mapping action to reveal a goal card that has not been explored yet.\n
        Args:
            legal_actions (list): List of legal actions available to the player.
            seen (list): List of seen card positions and their visibility status.
            revealed (list): List of cards that have been revealed on the board.
        Returns:
            list: A list containing the mapping action to reveal an unexplored goal card.
        """
        map_actions = [action for action in legal_actions if action.startswith('map')]
        aim = None

        # Pick a card that has not been looked at
        for pos in gc.GOAL_POSITIONS:
            if pos not in [item[0] for item in seen] and pos not in revealed:
                aim = pos
                break

        # Find the action to match the card that has not been looked at
        for map_action in map_actions:
            parts = map_action.split("-")
            coordinates = (int(parts[-2]), int(parts[-1]))
            if coordinates == aim:
                return [map_action]
