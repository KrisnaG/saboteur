"""
Author:
    Krisna Gusti (kgusti@myune.edu.au)
"""

from src.environment.saboteur_environment import SaboteurEnvironment
from src.program.common_behaviour import find_goal_card_aim, evaluate_state, euclidean_distance, infer_gold, \
    sabotage_player, mend_player, map_for_gold


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
        action = mend_player(legal_actions, turn, player['sabotaged'], kb, 'gold-miner')
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
        action = sabotage_player(legal_actions, turn, kb, 'saboteur', 0.6)
        if action is not None:
            return action

    # Pass
    return [choose_card_to_discard(legal_actions, gold_seen)]
