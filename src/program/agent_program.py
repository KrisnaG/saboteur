"""
Author:
    Krisna Gusti (kgusti@myune.edu.au)
"""
import random
import traceback

from src.environment.saboteur_environment import SaboteurEnvironment
import src.constant.game_constants as gc


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

def intelligent_agent(percepts, actuators):
    return []
