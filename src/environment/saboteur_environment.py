from une_ai.models import GameEnvironment
from une_ai.models import GridMap
import constant.game_constants as gc
import random

class SaboteurEnvironment(GameEnvironment):
    def __init__(self, game_board):
        super().__init__("Saboteur Game Environment")
        self._game_board = game_board
        self._player_turn = f'P{random.randint(0, gc.NUMBER_OF_PLAYERS)}'
        self._number_of_saboteur = random.randrange(2, 4)
        self._chosen_saboteurs = random.sample(list(range(gc.NUMBER_OF_PLAYERS)), self._number_of_saboteur)
    
    def get_players(self):
        return self._players
    
    def add_player(self, player):
        assert len(self._players) < gc.NUMBER_OF_PLAYERS, f"It is not possible to add more than {gc.NUMBER_OF_PLAYERS} players for this game."
        
        player_number = len(self._players)
        player_type = "gold-miner"
        
        if player_number in self._chosen_saboteurs:
            player_type = "saboteur"
        
        self._players[f'P{player_number}'] = (player, player_type)
        
        return player
    
    
    def get_game_state(self):
        game_state = {
            'game-board': self._game_board,
            'player-turn': self._player_turn
        }

        return game_state
    
    
    def get_legal_actions(game_state):
        pass
    
    
    def get_percepts(self):
        game_state = self.get_game_state()
        return {
            'game-board-sensor': game_state['game-board'],
            'turn-taking-indicator': self._player_turn
        }
        
        
    def get_winner(game_state):
        pass
    
    
    def is_terminal(game_state):
        pass
    
    
    def payoff(game_state, player_name):
        pass
        
        
    def state_transition(self, agent_actuators):
        pass
    
    
    def transition_result(game_state, action):
        pass
        
    
    def turn(game_state):
        return game_state['player-turn']