"""
Author:
    Krisna Gusti (kgusti@myune.edu.au)
"""
import random
import traceback

import numpy as np
from pomegranate.distributions import Categorical
from pomegranate.hmm import DenseHMM

from src.environment.saboteur_environment import SaboteurEnvironment
import src.constant.game_constants as gc
from src.exception.invalid_action_exception import InvalidActionException
from src.program.gold_miner_behaviour import gold_miner_behaviour
from src.program.saboteur_behaviour import saboteur_behaviour


# A simple agent program choosing actions randomly
def random_behaviour(percepts, actuators):
    try:
        player = {
            'player': percepts['player-sensor'],
            'player-type': percepts['player-type-sensor'],
            'hand': percepts['hand-sensor'],
            'sabotaged': percepts['sabotaged-sensor'],
            'seen': percepts['seen-sensor']
        }
        players = {f'P{i}': None for i in range(gc.NUMBER_OF_PLAYERS)}
        player_turn = percepts['turn-taking-indicator']
        players[player_turn] = player

        game_state = {
            'game-board': percepts['game-board-sensor'],
            'player-turn': player_turn,
            'players': players,
            'deck': percepts['deck-sensor'],
            'revealed': percepts['revealed-sensor']
        }

    except KeyError:
        game_state = {}
        print("You may have forgotten to add the necessary sensors:")
        traceback.print_exc()
    if not SaboteurEnvironment.is_terminal(game_state):
        legal_moves = SaboteurEnvironment.get_legal_actions(game_state)
        try:
            action = random.choice(legal_moves)
        except IndexError:
            print("You may have forgotten to implement the ConnectFourEnvironment methods, or you implemented them "
                  "incorrectly:")
            traceback.print_exc()
            return []

        if action.split('-')[0] == 'pass':
            action = random.choice(legal_moves)

        return [action]
    else:
        return []


def build_knowledge_base(players_actions):
    model = DenseHMM()
    states = ['gold-miner', 'saboteur']

    # Define emission probability distributions for each state
    # 'path', 'dead-end', 'sabotage', 'mend', 'map', 'dynamite', 'pass'
    gold_miner_emissions = [Categorical([[0.9, 0.001, 0.3, 0.4, 0.3, 0.5, 0.5]])]
    saboteur_emissions = [Categorical([[0.8, 0.95, 0.8, 0.2, 0.3, 0.7, 0.5]])]
    state_dists = gold_miner_emissions + saboteur_emissions

    model.add_distributions(state_dists)

    # Set initial probabilities
    model.add_edge(model.start, state_dists[0], 0.625)
    model.add_edge(model.start, state_dists[1], 0.375)

    # Set transition probabilities
    model.add_edge(state_dists[0], state_dists[0], 0.8)
    model.add_edge(state_dists[0], state_dists[1], 0.7)
    model.add_edge(state_dists[1], state_dists[1], 0.4)
    model.add_edge(state_dists[1], state_dists[0], 0.6)

    predicted_states = {}
    for player, actions in players_actions.items():
        if len(actions) > 1:
            observations = []
            for action in actions:
                if action.find('dead-end') >= 0:
                    observations.append('dead-end')
                if action.startswith('turn'):
                    observations.append('path')
                else:
                    observations.append(action.split('-')[0])

            X = np.array([[[['path', 'dead-end', 'sabotage', 'mend', 'map', 'dynamite', 'pass'].index(label)]
                           for label in observations]])

            # Making a prediction of the most likely sequence of states
            y_hat = model.predict(X)
            predicted_states[player] = [states[y] for y in y_hat[0].tolist()][-1]
        else:
            predicted_states[player] = 'gold-miner'

    return predicted_states


def intelligent_agent(percepts, actuators):
    player = {
        'player': percepts['player-sensor'],
        'player-type': percepts['player-type-sensor'],
        'hand': percepts['hand-sensor'],
        'sabotaged': percepts['sabotaged-sensor'],
        'seen': percepts['seen-sensor']
    }

    players = {f'P{i}': None for i in range(gc.NUMBER_OF_PLAYERS)}
    player_turn = percepts['turn-taking-indicator']
    players[player_turn] = player
    players_actions = percepts['players-actions-sensor']

    game_state = {
        'game-board': percepts['game-board-sensor'],
        'player-turn': player_turn,
        'players': players,
        'deck': percepts['deck-sensor'],
        'revealed': percepts['revealed-sensor'],
        'players-actions': players_actions
    }

    kb = build_knowledge_base(players_actions)

    print(f"{player_turn}: {kb}")

    if player['player-type'] == 'saboteur':
        action = saboteur_behaviour(game_state, kb)
    else:
        action = gold_miner_behaviour(game_state, kb)

    if action is None or len(action) <= 0:
        print("ERROR")
        gold_miner_behaviour(game_state, kb)
        raise InvalidActionException(f"No action for player {player_turn}")

    return action
