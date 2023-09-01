"""
Author:
    Krisna Gusti (kgusti@myune.edu.au)
"""

import os
import shutil

from game.saboteur_game import SaboteurGame
from environment.saboteur_environment import SaboteurEnvironment
from player.saboteur_player import SaboteurPlayer
from program.agent_program import intelligent_agent, random_behaviour
from component.game_board import GameBoard
from component.deck import Deck
import constant.game_constants as gc


def delete_pycache(root_dir):
    """
    Recursively delete __pycache__ directories from the specified directory.\n
    Args:
        root_dir (str): The root directory to start the search for __pycache__ directories.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            if dirname == '__pycache__':
                pycache_path = os.path.join(dirpath, dirname)
                shutil.rmtree(pycache_path)


if __name__ == '__main__':
    """
    Main entry point.
    """
    game_board = GameBoard()
    deck = Deck()

    # Set game environment
    game_environment = SaboteurEnvironment(game_board, deck)
    
    # Create SaboteurPlayer instances for each player
    for player_number in range(gc.NUMBER_OF_PLAYERS):
        game_environment.add_player(SaboteurPlayer(f'P{player_number}', random_behaviour))

    game = SaboteurGame(game_environment)

    # Delete cache files
    delete_pycache("../src")
