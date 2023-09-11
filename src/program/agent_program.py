"""
Author:
    Krisna Gusti (kgusti@myune.edu.au)
"""

import random
import traceback

import numpy as np
from pomegranate.distributions import Categorical
from pomegranate.hmm import DenseHMM

from environment.saboteur_environment import SaboteurEnvironment
import constant.game_constants as gc
from exception.invalid_action_exception import InvalidActionException
from program.gold_miner_behaviour import GoldMinerBehaviour
from program.saboteur_behaviour import SaboteurBehaviour


def random_behaviour(percepts, actuators):
    """
    A basic agent program that selects actions randomly from the legal moves available to the player.\n
    Args:
        percepts (dict): A dictionary containing sensor data including player information and game state.
        actuators (dict): A dictionary containing actuator data.
    Returns:
        list: A list of actions to be taken by the agent.
    """
    try:
        # Extract player information
        player = {
            'player': percepts['player-sensor'],
            'player-type': percepts['player-type-sensor'],
            'hand': percepts['hand-sensor'],
            'sabotaged': percepts['sabotaged-sensor'],
            'seen': percepts['seen-sensor']
        }

        # Initialise a dictionary to represent all players in the game
        players = {f'P{i}': None for i in range(gc.NUMBER_OF_PLAYERS)}

        # Set the current player's data in the players dictionary
        player_turn = percepts['turn-taking-indicator']
        players[player_turn] = player

        # Create a game state dictionary with player and game information
        game_state = {
            'game-board': percepts['game-board-sensor'],
            'player-turn': player_turn,
            'players': players,
            'deck': percepts['deck-sensor'],
            'revealed': percepts['revealed-sensor']
        }

    except KeyError:
        # Handle exceptions related to missing sensors
        game_state = {}
        print("You may have forgotten to add the necessary sensors:")
        traceback.print_exc()

    if not SaboteurEnvironment.is_terminal(game_state):
        legal_moves = SaboteurEnvironment.get_legal_actions(game_state)
        try:
            # Randomly select an action from the legal moves
            action = random.choice(legal_moves)
        except IndexError:
            print("You may have forgotten to implement the ConnectFourEnvironment methods, or you implemented them "
                  "incorrectly:")
            traceback.print_exc()
            return []

        if percepts['deck-sensor'].cards_remaining() > 0:
            return [action, 'draw-True']
        else:
            return [action, 'draw-False']
    else:
        return []


def build_knowledge_base(players_actions, current_player, player_type):
    """
    Build a knowledge base to predict whether each player is a Gold Miner or a Saboteur based on their actions.\n
    Args:
        players_actions (dict): A dictionary mapping player names to their lists of actions.
        current_player (string): The current player.
        player_type (string) the player type ('gold-miner' or 'saboteur')
    Returns:
        dict: A dictionary mapping player names to their predicted roles ('gold-miner' or 'saboteur').
    """
    model = DenseHMM()
    states = ['gold-miner', 'saboteur']

    # Define emission probability distributions for each state
    # 'path', 'dead-end', 'sabotage', 'mend', 'map', 'dynamite', 'pass'
    gold_miner_emissions = [Categorical([[0.9, 0.0, 0.3, 0.5, 0.6, 0.5, 0.5]])]
    saboteur_emissions = [Categorical([[0.8, 0.99, 0.6, 0.3, 0.4, 0.6, 0.5]])]
    state_dists = gold_miner_emissions + saboteur_emissions

    model.add_distributions(state_dists)

    # Set initial probabilities 0 = gold-miner 1 = saboteur
    model.add_edge(model.start, state_dists[0], 0.625)
    model.add_edge(model.start, state_dists[1], 0.375)

    # Set transition probabilities 0 = gold-miner 1 = saboteur
    model.add_edge(state_dists[0], state_dists[0], 0.8)
    model.add_edge(state_dists[0], state_dists[1], 0.7)
    model.add_edge(state_dists[1], state_dists[1], 0.7)
    model.add_edge(state_dists[1], state_dists[0], 0.5)

    predicted_states = {}

    # Iterate over each player's actions and build predictions
    for player, actions in players_actions.items():
        if len(actions) > 1:
            observations = []

            # Process each action to extract relevant observations
            for action in actions:
                if action.find('dead-end') >= 0:
                    observations.append('dead-end')
                if action.startswith('turn'):
                    observations.append('path')
                else:
                    observations.append(action.split('-')[0])

            # Prepare the observations for prediction
            X = np.array([[[['path', 'dead-end', 'sabotage', 'mend', 'map', 'dynamite', 'pass'].index(label)]
                           for label in observations]])

            # Making a prediction of the most likely sequence of states
            y_hat = model.predict(X)
            predicted_states[player] = [states[y] for y in y_hat[0].tolist()][-1]
        else:
            predicted_states[player] = 'gold-miner'

    predicted_states[current_player] = player_type

    return predicted_states


def intelligent_agent(percepts, actuators):
    """
    The intelligent agent function takes percepts and performs actions based on the game state and player type.\n
    Args:
        percepts (dict): A dictionary containing sensor data including player information, game state, and actions.
        actuators (dict): A dictionary containing actuator data.
    Returns:
        list: A list of actions to be taken by the agent.
    """
    # Extract player information
    player = {
        'player': percepts['player-sensor'],
        'player-type': percepts['player-type-sensor'],
        'hand': percepts['hand-sensor'],
        'sabotaged': percepts['sabotaged-sensor'],
        'seen': percepts['seen-sensor']
    }

    # Initialise a dictionary to represent all players in the game
    players = {f'P{i}': None for i in range(gc.NUMBER_OF_PLAYERS)}

    # Set the current player's data in the players dictionary
    player_turn = percepts['turn-taking-indicator']
    players[player_turn] = player

    # Extract game state information
    players_actions = percepts['players-actions-sensor']
    deck = percepts['deck-sensor']
    game_state = {
        'game-board': percepts['game-board-sensor'],
        'player-turn': player_turn,
        'players': players,
        'deck': deck,
        'revealed': percepts['revealed-sensor'],
        'players-actions': players_actions,
        'announcements': percepts['announcements-sensor']
    }

    # Build the knowledge base based on players' action
    kb = build_knowledge_base(players_actions, player_turn, player['player-type'])
    print(f"{player_turn} KB: {kb}")

    # Choose actions based on the player's type (saboteur or gold miner)
    if player['player-type'] == 'saboteur':
        actions = SaboteurBehaviour.behaviour(game_state, kb)
    else:
        actions = GoldMinerBehaviour.behaviour(game_state, kb)

    # Handle errors and ensure that an action is returned
    if actions is None or len(actions) <= 0:
        raise InvalidActionException(f"No action for player {player_turn}")

    # Draw a card if there are any remaining
    if deck.cards_remaining() > 0:
        actions.append('draw-True')
    elif actuators['draw-card']:
        actions.append('draw-False')

    return actions
