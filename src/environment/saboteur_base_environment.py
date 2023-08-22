from une_ai.models import GameEnvironment
from une_ai.models import GridMap
import constant.game_constants as gc

class SaboteurBaseEnvironment(GameEnvironment):
    def __init__(self):
        super().__init__("Saboteur Game Environment")
        self._game_board = GridMap(gc.BOARD_COL_SIZE, gc.BOARD_ROW_SIZE, None)
        self._player_turn = gc.STARTING_PLAYER
    
    
    def add_player(self, player):
        assert len(self._players) < gc.NUMBER_OF_PLAYERS, f"It is not possible to add more than {gc.NUMBER_OF_PLAYERS} players for this game."

        player = f'P{len(self._players)}'
        
        self._players[player] = player
        
        return player
    
    
    def get_game_state(self):
        game_state = {
            'game-board': self._game_board.copy(),
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