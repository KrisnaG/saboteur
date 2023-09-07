"""
Author:
    Krisna Gusti (kgusti@myune.edu.au)
"""

import math

from src.component.game_board import GameBoard
from src.environment.saboteur_environment import SaboteurEnvironment
import src.constant.game_constants as gc


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
    distance = euclidean_distance(aim[0], x, aim[1], y)
    payoff += 2 / (1 + distance)

    # If the distance is 1 (adjacent position), add a bonus to the payoff
    if distance == 1:
        payoff += 1.5

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
                    payoff += 1.0
                elif GameBoard.opposite_direction(direction) == n_direction:
                    payoff -= 0.5
                else:
                    payoff += 0.5

    return payoff


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


def find_goal_card_aim(seen, revealed):
    """
    Determine the aim or target position for a goal card placement based on the current state of seen and
    revealed cards.\n
    Args:
        seen (list): A list of tuples containing positions and a bool indicating if the card at that position is seen.
        revealed (list): A list of positions where cards have been revealed.
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

    # Can we infer were the gold is?
    inferred = infer_gold(seen, revealed)
    if len(inferred) == 1:
        return inferred[0]

    return aim


def find_best_path_card_placement(game_state, legal_actions, player, revealed):
    """
    Find the best path card placement action based on the current game state and available legal actions.\n
    Args:
        game_state (dict): The current game state.
        legal_actions (list): List of legal actions the player can take.
        player (dict): Player information including seen cards.
        revealed (list): List of revealed card positions.
    Returns:
        list: A list containing the best path card placement action to achieve the player's goal.
    """
    path_actions = [action for action in legal_actions
                    if (action.startswith('path') or action.startswith('turn')) and action.find('dead') < 0]
    action = None

    aim = find_goal_card_aim(player['seen'], revealed)

    # Has someone announced they've seen a gold card?
    #   Do we trust the player that made the announcement?

    payoff_best = float('-Inf')

    # Find best card to reach the aim card
    for path_action in path_actions:
        future_state, _ = SaboteurEnvironment.transition_result(game_state, path_action)
        payoff = evaluate_state(future_state['game-board'], aim, path_action)
        if payoff > payoff_best:
            payoff_best = payoff
            action = path_action

    return [action]


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


def mend_player(legal_actions, player, sabotaged_players, kb):
    """
    Determine the appropriate mend action for the player based on their current state and knowledge.\n
    Args:
        legal_actions (list): List of legal actions available to the player.
        player (str): The player for whom mend actions are being considered.
        sabotaged_players (list): List of players who are sabotaged.
        kb (dict): Knowledge base containing player roles (gold-miner or saboteur).
    Returns:
        list or None: A list containing the mend action for the player, or None if no mend action is taken.
    """
    mend_actions = [action for action in legal_actions if action.startswith('mend')]

    # Is the current player sabotaged?
    if player in sabotaged_players:
        return [action for action in mend_actions if action.endswith(player)]

    # What other players are sabotaged?
    for other_player in sabotaged_players:
        # Do we trust the player that is sabotaged?
        if kb[other_player] == 'gold-miner':
            return [action for action in mend_actions if action.endswith(other_player)]

    # If we don't trust any sabotaged players, don't take any mend actions
    return None


def sabotage_player(legal_actions, player, kb):
    """
    Determine the appropriate sabotage action for the player based on their knowledge and suspicions.\n
    Args:
        legal_actions (list): List of legal actions available to the player.
        player (str): The player who wants to take a sabotage action.
        kb (dict): Knowledge base containing player roles (gold-miner or saboteur).
    Returns:
        list or None: A list containing the sabotage action for the player, or None if no sabotage action is taken.
    """
    sabotage_actions = [action for action in legal_actions if action.startswith('sabotage')]

    # Who can we sabotage?
    for action in sabotage_actions:
        other_player = action.split('-')[1]
        if other_player == player:
            continue
        # Do we suspect the player being a saboteur?
        if kb[other_player] == 'saboteur':
            return [action]

    # If we don't suspect any saboteur players, don't take any sabotage actions
    return None


def dynamite_blocked_path(legal_actions, game_board, aim):
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
        if card.get_path_type().startswith('dead-end'):
            new_distance = euclidean_distance(x, aim[0], y, aim[1])
            if new_distance < distance:
                distance = new_distance
                action = [dynamite_action]

    # If we can't find any blocked paths, don't take any sabotage actions
    return action


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

    dead_end_card = [string for string in pass_actions if 'dead-end' in string]
    if len(dead_end_card) > 0:
        return dead_end_card[0]

    map_card = [string for string in pass_actions if 'map' in string]
    if len(map_card) > 0 and gold_seen:
        return map_card[0]

    dynamite_card = [string for string in pass_actions if 'dynamite' in string]
    if len(dynamite_card) > 0:
        return dynamite_card[0]

    sabotage_card = [string for string in pass_actions if 'sabotage' in string]
    if len(sabotage_card) > 0:
        return sabotage_card[0]

    mend_card = [string for string in pass_actions if 'mend' in string]
    if len(mend_card) > 0:
        return mend_card[0]

    if len(map_card) > 0:
        return map_card[0]

    return pass_actions[0]


def gold_miner_behaviour(game_state, kb):
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

    # Path
    path_exists = any((("path" in action or "turn" in action) and action.find('dead') < 0 and action.find('pass') < 0)
                      for action in legal_actions)
    if path_exists:
        return find_best_path_card_placement(game_state, legal_actions, player, revealed_cards)

    # Map
    map_exists = any("map" in action and action.find('pass') < 0 for action in legal_actions)
    gold_seen = len([seen_item for seen_item in seen if seen_item[1]]) > 0
    can_infer_gold = len(infer_gold(seen, revealed_cards)) == 1
    if map_exists and not gold_seen and not can_infer_gold:
        return map_for_gold(legal_actions, seen, revealed_cards)

    # Mend
    mend_exists = any("mend" in action and action.find('pass') < 0 for action in legal_actions)
    if mend_exists and len(player['sabotaged']) > 0:
        action = mend_player(legal_actions, turn, player['sabotaged'], kb)
        if action is not None:
            return action

    # Dynamite
    dynamite_exists = any("dynamite" in action and action.find('pass') < 0 for action in legal_actions)
    if dynamite_exists:
        action = dynamite_blocked_path(legal_actions, game_state['game-board'],
                                       find_goal_card_aim(seen, game_state['revealed']))
        if action is not None:
            return action

    # Sabotage
    sabotage_exists = any("sabotage" in action and action.find('pass') < 0 for action in legal_actions)
    if sabotage_exists:
        action = sabotage_player(legal_actions, turn, kb)
        if action is not None:
            return action

    # Pass
    return [choose_card_to_discard(legal_actions, gold_seen)]
