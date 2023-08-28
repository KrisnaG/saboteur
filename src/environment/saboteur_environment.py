from une_ai.models import GameEnvironment
from une_ai.models import GridMap
import src.constant.game_constants as gc
from src.component.card import ActionCard, PathCard
from src.component.game_board import GameBoard
import random


class SaboteurEnvironment(GameEnvironment):
    def __init__(self, game_board, deck):
        super().__init__("Saboteur Game Environment")
        self._game_board = game_board
        self._player_turn = f'P{random.randrange(0, gc.NUMBER_OF_PLAYERS)}'
        self._number_of_saboteur = random.randrange(2, 4)
        self._chosen_saboteurs = random.sample(list(range(gc.NUMBER_OF_PLAYERS)), self._number_of_saboteur)
        self._deck = deck

    def _change_player(self):
        """
        Change to the next player.
        """
        current_number = int(self._player_turn[1:])
        next_number = (current_number + 1) % gc.NUMBER_OF_PLAYERS
        self._player_turn = f'P{next_number}'


    def get_deck(self):
        """
        Get the deck for the current environment.
        """
        return self._deck


    def get_players(self):
        """
        Get the players for the current environment.
        """
        return self._players


    def add_player(self, player):
        """
        Add a player to the environment.
        Args:
            player (SaboteurPlayer): Player to add.
        Returns:
            The player that was added.
        """
        assert len(self._players) < gc.NUMBER_OF_PLAYERS, f"It is not possible to add more than {gc.NUMBER_OF_PLAYERS} players for this game."

        player_number = len(self._players)
        player_type = "gold-miner"

        if player_number in self._chosen_saboteurs:
            player_type = "saboteur"

        hand, sabotaged = [], []

        self._players[f'P{player_number}'] = {
            player: player,
            player_type: player_type,
            hand: hand,
            sabotaged: sabotaged
        }

        return player


    def get_game_state(self):
        """
            Get the current environment game state.
        Returns:
            Current environment game state.
        """
        game_state = {
            'game-board': self._game_board,
            'player-turn': self._player_turn,
            'players': self._players,
            'deck': self._deck
        }

        return game_state


    def get_legal_actions(game_state):
        """
        Get the list of legal actions based on the current game state.\n
        Args:
            game_state (dict): The current game state.
        Returns:
            list: A list of legal actions.
        """
        legal_actions = []

        game_board = game_state['game-board']
        players = game_state['players']
        turn = game_state['player-turn']
        player = players[turn]
        hand = player['hand']
        sabotaged = player['sabotaged']

        path_cards = [card for card in hand if isinstance(card, PathCard)]
        action_cards = [card for card in hand if isinstance(card, ActionCard)]

        # Cannot play path cards if sabotaged
        if len(sabotaged) > 0:
            mend_actions = []
            for card in action_cards:
                if card.get_action() == 'mend':
                    mend_actions.append('mend')
                    if len(mend_actions) >= len(sabotaged):
                        break
            legal_actions = legal_actions + mend_actions
        else:
            # Path cards
            for y, row in enumerate(game_board.get_board_map()):
                for x, cell in enumerate(row):
                    if cell is None:
                        for path_card in path_cards:
                            # Check card placements
                            if GameBoard.can_place_card(x, y, path_card, game_board.get_board()):
                                legal_actions.append(f'path-{x}-{y}-{path_card.get_path_type()}')

                            # Turn card and check placements
                            turned_card = PathCard(path_card.get_tunnels())
                            turned_card.turn_card()
                            if GameBoard.can_place_card(x, y, turned_card, game_board.get_board()):
                                legal_actions.append(f'turn-{x}-{y}-{path_card.get_path_type()}')

        # Sabotage
        for card in action_cards:
            action = card.get_action()
            if action == 'sabotage':
                for opponent in players:
                    if opponent != turn:
                        legal_actions.append(f'sabotage-{opponent}')

        # Map and dynamite
        for y, row in enumerate(game_board.get_board_map()):
            for x, cell in enumerate(row):
                if cell is not None:
                    for card in action_cards:
                        action = card.get_action()
                        if cell.is_special_card() and not cell.is_revealed() and action == 'map':
                            legal_actions.append(f'map-{x}-{y}')
                        elif not cell.is_special_card() and action == 'dynamite':
                            legal_actions.append(f'dynamite-{x}-{y}')

        # Pass and discard
        if len(hand) > 0:
            for card in hand:
                if isinstance(card, PathCard):
                    legal_actions.append(f'pass-path-{card.get_path_type()}')
                else:
                    legal_actions.append(f'pass-{card.get_action}')

        return legal_actions


    def get_percepts(self):
        game_state = self.get_game_state()
        return {
            'game-board-sensor': game_state['game-board'],
            'turn-taking-indicator': self._player_turn,
            'player': self._players[self._player_turn]
        }


    def get_winner(game_state):
        pass


    def is_terminal(game_state):
        pass


    def payoff(game_state, player_name):
        pass


    def state_transition(self, agent_actuators):
        # Check actuator

        # Place card

        # Change player

        # Reveal any special cards?
        pass


    def transition_result(game_state, action):
        # Path

        # Sabotage

        # Dynamite

        # Map

        # Pass

        pass


    def turn(game_state):
        return game_state['player-turn']
