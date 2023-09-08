"""
Author:
    Krisna Gusti (kgusti@myune.edu.au)
"""
from src.component.game_board import GameBoard
from src.environment.saboteur_environment import SaboteurEnvironment
from src.program.common_behaviour import CommonBehaviour


class SaboteurBehaviour(CommonBehaviour):
    """
    Behaviour for a Saboteur agent.
    """

    @staticmethod
    def evaluate_bad_state(game_board, aim, action):
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
        distance = SaboteurBehaviour.euclidean_distance(aim[0], x, aim[1], y)
        payoff += 4 / (1 + distance)

        # If the distance is 1 (adjacent position), minus a bonus to the payoff
        if distance == 1:
            payoff -= 0.5

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
        elif y < aim[1]:
            direction = "west"
        elif y > aim[1]:
            direction = "east"

        # Evaluate the payoff based on available tunnels and direction
        for n_direction, location in neighbours.items():
            nx, ny = location
            if GameBoard.is_on_board(nx, ny):
                n_card = game_board.get_board().get_item_value(nx, ny)
                if n_card is None and n_direction in tunnels:
                    if direction == n_direction:
                        payoff -= 1.5
                    elif GameBoard.opposite_direction(direction) == n_direction:
                        payoff += 1.0
                    else:
                        payoff -= 0.2

        return payoff

    @staticmethod
    def find_best_path_card_placement(game_state, legal_actions, player, revealed, kb):
        """
        Find the best path card placement action based on the current game state and available legal actions.\n
        Args:
            game_state (dict): The current game state.
            legal_actions (list): List of legal actions the player can take.
            player (dict): Player information including seen cards.
            revealed (list): List of revealed card positions.
            kb (dict): The knowledge base containing information about other players.
        Returns:
            list: A list containing the best path card placement action to achieve the player's goal.
        """
        path_actions = [action for action in legal_actions
                        if action.startswith('path') or action.startswith('turn')]
        action = None

        aim = SaboteurBehaviour.find_goal_card_aim(player['seen'], revealed, game_state['announcements'], kb)

        # Has someone announced they've seen a gold card?
        #   Do we trust the player that made the announcement?

        payoff_best = float('-Inf')

        # Find best card to sabotage the aim
        for path_action in path_actions:
            future_state, _ = SaboteurEnvironment.transition_result(game_state, path_action)
            if path_action.find('dead') > 0:
                payoff = SaboteurBehaviour.evaluate_state(future_state['game-board'], aim, path_action)
                parts = path_action.split("-")
                payoff += (len(parts) - 3)
            else:
                payoff = SaboteurBehaviour.evaluate_bad_state(future_state['game-board'], aim, path_action)

            if payoff > payoff_best:
                payoff_best = payoff
                action = path_action

        return [action]

    @staticmethod
    def dynamite_path(legal_actions, game_board, aim):
        """
        Determine if a dynamite action is needed to clear a blocked path to the goal.\n
        Args:
            legal_actions (list): List of legal actions available to the player.
            game_board: The current game board.
            aim (tuple): Coordinates of the goal card.
        Returns:
            list or None: A list containing the dynamite action to clear a blocked path, or None if no action is needed.
        """
        dynamite_actions = [action for action in legal_actions if action.startswith('dynamite')]
        distance = float('+Inf')
        action = None

        # Is this a path that has been blocked with a dead end?
        for dynamite_action in dynamite_actions:
            parts = dynamite_action.split('-')
            x = int(parts[1])
            y = int(parts[2])
            card = game_board.get_board().get_item_value(x, y)
            if not card.get_path_type().startswith('dead-end'):
                new_distance = SaboteurBehaviour.euclidean_distance(x, aim[0], y, aim[1])
                if new_distance < distance:
                    distance = new_distance
                    action = [dynamite_action]

        # If we can't find any blocked paths, don't take any sabotage actions
        return action

    @staticmethod
    def choose_card_to_discard(legal_actions, gold_seen):
        """
        Determine which card to discard from available legal actions.\n
        Args:
            legal_actions (list): List of legal actions available to the player.
            gold_seen (bool): Indicates if a gold card has been seen.
        Returns:
            str: The selected card to discard.
        """
        pass_actions = [action for action in legal_actions if action.startswith('pass')]

        map_card = [string for string in pass_actions if 'map' in string]
        if len(map_card) > 0 and gold_seen:
            return map_card[0]

        mend_card = [string for string in pass_actions if 'mend' in string]
        if len(mend_card) > 0:
            return mend_card[0]

        if len(map_card) > 0:
            return map_card[0]

        dynamite_card = [string for string in pass_actions if 'dynamite' in string]
        if len(dynamite_card) > 0:
            return dynamite_card[0]

        sabotage_card = [string for string in pass_actions if 'sabotage' in string]
        if len(sabotage_card) > 0:
            return sabotage_card[0]

        return pass_actions[0]

    @staticmethod
    def behaviour(game_state, kb):
        """
        Determine the behavior of a Gold Miner player based on the game state and knowledge base (kb).\n
        Args:
            game_state (dict): The current game state.
            kb (dict): The knowledge base containing information about other players.
        Returns:
            list: A list of actions to be taken by the Gold Miner player.
        """
        turn = game_state['player-turn']
        player = game_state['players'][turn]
        revealed_cards = game_state['revealed']
        seen = player['seen']

        legal_actions = SaboteurEnvironment.get_legal_actions(game_state)

        # Dynamite
        dynamite_exists = any("dynamite" in action and action.find('pass') < 0 for action in legal_actions)
        if dynamite_exists:
            action = SaboteurBehaviour.dynamite_path(
                legal_actions, game_state['game-board'],
                SaboteurBehaviour.find_goal_card_aim(seen, game_state['revealed'], game_state['announcements'], kb))
            if action is not None:
                return action

        # Sabotage
        sabotage_exists = any("sabotage" in action and action.find('pass') < 0 for action in legal_actions)
        if sabotage_exists:
            action = SaboteurBehaviour.sabotage_player(legal_actions, turn, kb, 'gold-miner', 0.9)
            if action is not None:
                return action

        # Map
        map_exists = any("map" in action and action.find('pass') < 0 for action in legal_actions)
        gold_seen = len([seen_item for seen_item in seen if seen_item[1]]) > 0
        can_infer_gold = len(SaboteurBehaviour.infer_gold(seen, revealed_cards)) == 1
        if map_exists and not gold_seen and not can_infer_gold:
            return SaboteurBehaviour.map_for_gold(legal_actions, seen, revealed_cards)

        # Path
        path_exists = any((("path" in action or "turn" in action) and action.find('pass') < 0)
                          for action in legal_actions)
        if path_exists:
            return SaboteurBehaviour.find_best_path_card_placement(
                game_state, legal_actions, player, revealed_cards, kb)

        # Mend
        mend_exists = any("mend" in action and action.find('pass') < 0 for action in legal_actions)
        if mend_exists and len(player['sabotaged']) > 0:
            action = SaboteurBehaviour.mend_player(legal_actions, turn, player['sabotaged'], kb, 'saboteur')
            if action is not None:
                return action

        # Pass
        return [SaboteurBehaviour.choose_card_to_discard(legal_actions, gold_seen)]
