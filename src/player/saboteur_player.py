from une_ai.models import Agent, GridMap
import constant.game_constants as gc
from component.game_board import GameBoard
from component.card import Card

class SaboteurPlayer(Agent):
    
    def __init__(self, agent_name, agent_program):
        super().__init__(agent_name, agent_program)
        
    def add_all_sensors(self):
        """ Adds all the required sensors.
            Sensors: 
        """
        # Game Board sensor
        self.add_sensor(
            sensor_name='game-board-sensor',
            initial_value=GameBoard(),
            validation_function=lambda game_board: 
                isinstance(game_board, GameBoard) and 
                all(
                    isinstance(cell, (Card, type(None))) for row in game_board.get_board_map() for cell in row)
        )
    
    def add_all_actuators(self):
        pass
    
    def add_all_actions(self):
        pass