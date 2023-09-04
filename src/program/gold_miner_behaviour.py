"""
Gold-diggers will prioritize building the shortest path to a goal card, aiming to reach the treasure efficiently.
If a player knows the location of the gold (through a map card or reliable information from another player),
they will actively try to construct a path to the gold card. Gold-diggers may use the information provided by other
players about goal cards to determine if they are sincere or lying. This can help them make inferences about the
other player's role. When distrustful of another player, suspecting them of being a saboteur, gold-diggers may
strategically use sabotage cards against them. Conversely, if gold-diggers trust another player, considering them a
fellow gold-digger, they may use a mend card to help them if they are under the effect of a sabotage card.
Gold-diggers can keep track of drawn and played cards to predict which path cards are remaining in the deck and the
hands of other players, guiding their decision-making process towards reaching the gold. However, there may be
additional uncertainty due to discarded cards. They may deploy the dynamite card to remove dead-ends from paths that
could potentially lead to the gold cards.
"""
import math

from src.component.game_board import GameBoard
from src.environment.saboteur_environment import SaboteurEnvironment
import src.constant.game_constants as gc

def euclidean_distance(x1, x2, y1, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def evaluate_state(game_board, aim, action):
    parts = action.split('-')
    x = int(parts[1])
    y = int(parts[2])
    payoff = 0

    distance = euclidean_distance(aim[0], x, aim[1], y)
    payoff += 2 / (1 + distance)

    if distance == 1:
        payoff += 1.5

    card = game_board.get_board().get_item_value(x, y)
    tunnels = [item for sublist in card.get_tunnels() for item in sublist]

    neighbours = {
        'north': (x - 1, y),
        'south': (x + 1, y),
        'west': (x, y - 1),
        'east': (x, y + 1)
    }
    direction = ""

    if x < aim[0]:
        direction = "south"
    elif x > aim[0]:
        direction = "north"
    elif y < aim[1]:
        direction = "west"
    elif y > aim[1]:
        direction = "east"

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


def find_goal_card_aim(seen, revealed):
    aim = None

    # Aim for a card that has not been revealed
    for position in gc.GOAL_POSITIONS:
        if position not in revealed:
            aim = position
            break

    # Have we seen a gold card?
    gold_seen = [seen_item for seen_item in seen if seen_item[1]]
    if len(gold_seen) > 0:
        aim = gold_seen[0][0]

    return aim


def find_best_path_card_placement(game_state, legal_actions, player, revealed):
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


def map_for_gold(legal_actions, seen):
    map_actions = [action for action in legal_actions if action.startswith('map')]
    aim = None

    # Pick a card that has not been looked at
    for pos in gc.GOAL_POSITIONS:
        if pos not in [item[0] for item in seen]:
            aim = pos
            break

    # Find the action to match the card that has not been looked at
    for map_action in map_actions:
        parts = map_action.split("-")
        coordinates = (int(parts[-2]), int(parts[-1]))
        if coordinates == aim:
            return [map_action]


def mend_player(legal_actions, player, sabotaged_players, kb):
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
    turn = game_state['player-turn']
    player = game_state['players'][turn]
    seen = player['seen']

    legal_actions = SaboteurEnvironment.get_legal_actions(game_state)

    # Path
    path_exists = any((("path" in action or "turn" in action) and action.find('dead') < 0 and action.find('pass') < 0)
                      for action in legal_actions)
    if path_exists:
        return find_best_path_card_placement(game_state, legal_actions, player, game_state['revealed'])

    # Map
    map_exists = any("map" in action and action.find('pass') < 0 for action in legal_actions)
    gold_seen = len([seen_item for seen_item in seen if seen_item[1]]) > 0
    if map_exists and not gold_seen:
        return map_for_gold(legal_actions, seen)

    # Mend
    mend_exists = any("mend" in action and action.find('pass') < 0 for action in legal_actions)
    if mend_exists and len(player['sabotaged']) > 0:
        action = mend_player(legal_actions, turn, player['sabotaged'], kb)
        if action is not None:
            return action

    # Dynamite
    dynamite_exists = any("dynamite" in action and action.find('pass') < 0 for action in legal_actions)
    if dynamite_exists:
        action = dynamite_blocked_path(legal_actions, game_state['game-board'], find_goal_card_aim(seen, game_state['revealed']))
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
