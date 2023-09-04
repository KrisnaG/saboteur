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
import random

from src.component.game_board import GameBoard
from src.environment.saboteur_environment import SaboteurEnvironment
import src.constant.game_constants as gc


def evaluate_state(game_board, aim, action):
    parts = action.split('-')
    x = int(parts[1])
    y = int(parts[2])
    payoff = 0

    distance = math.sqrt((aim[0] - x)**2 + (aim[1] - y)**2)
    payoff += 2 / (1 + distance)

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
                    payoff += 0.75
                elif GameBoard.opposite_direction(direction) == n_direction:
                    payoff -= 0.5
                else:
                    payoff += 0.5

    return payoff


def find_best_path_card_placement(game_state, legal_actions, player, revealed):
    path_actions = [action for action in legal_actions
                    if (action.startswith('path') or action.startswith('turn')) and action.find('dead') < 0]
    action = None
    aim = None

    # Aim for a card that has not been revealed
    for position in gc.GOAL_POSITIONS:
        if position not in revealed:
            aim = position
            break

    # Have we seen a gold card?
    seen = player['seen']
    gold_seen = [seen_item for seen_item in seen if seen_item[1]]
    if len(gold_seen) > 0:
        aim = gold_seen[0][0]

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


def mend_player(legal_actions, player, sabotaged_players):
    mend_actions = [action for action in legal_actions if action.startswith('mend')]

    # Is the current player sabotaged?
    if player in sabotaged_players:
        return [action for action in mend_actions if action.endswith(player)]

    # What other players are sabotaged?
    #   Do we trust the player that is sabotaged?
    return None


def sabotage_player(legal_actions):
    sabotage_actions = [action for action in legal_actions if action.startswith('sabotage')]

    # Who can we sabotage?
    #   Do we suspect the player being a saboteur?


def dynamite_blocked_path(legal_actions):
    dynamite_actions = [action for action in legal_actions if action.startswith('dynamite')]

    # Is this a path that has been blocked with a dead end?


def buildKnowledgeBase():
    pass


def gold_miner_behaviour(game_state):
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
        action = mend_player(legal_actions, turn, player['sabotaged'])
        if action is not None:
            return action

    # Dynamite
    dynamite_exists = any("dynamite" in action and action.find('pass') < 0 for action in legal_actions)

    # Sabotage
    sabotage_exists = any("sabotage" in action and action.find('pass') < 0 for action in legal_actions)

    # If we cannot make any other moves pass
    # we may with to pass with a dead end card
    return [random.choice(legal_actions)]
