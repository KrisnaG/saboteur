"""
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""

from une_ai.models import GameEnvironment

import src.constant.game_constants as gc
from src.component.card import ActionCard, PathCard
from src.component.game_board import GameBoard
from src.exception.invalid_action_exception import InvalidActionException
from src.exception.invalid_move_exception import InvalidMoveException

import random


class SaboteurEnvironment(GameEnvironment):
    def __init__(self, game_board, deck):
        super().__init__("Saboteur Game Environment")
        self._game_board = game_board
        self._player_turn = f'P{random.randrange(0, gc.NUMBER_OF_PLAYERS)}'
        self._number_of_saboteur = random.randrange(2, 4)
        self._chosen_saboteurs = random.sample(list(range(gc.NUMBER_OF_PLAYERS)), self._number_of_saboteur)
        self._deck = deck
        self._revealed_goal_cards = []

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

        hand, sabotaged, seen = [], [], []

        self._players[f'P{player_number}'] = {
            'player': player,
            'player_type': player_type,
            'hand': hand,
            'sabotaged': sabotaged,
            'seen': seen
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
            'deck': self._deck,
            'revealed': self._revealed_goal_cards
        }

        return game_state

    @staticmethod
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
                            turned_card = PathCard(path_card.get_tunnels(), path_card.get_path_type())
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
            'players': self._players
        }

    @staticmethod
    def get_winner(game_state):
        pass

    @staticmethod
    def is_terminal(game_state):
        pass

    @staticmethod
    def payoff(game_state, player_name):
        pass

    @staticmethod
    def transition_result(game_state, action_str):
        # Extract action
        parts = action_str.split('-')
        action = parts[0]

        # Extract game state
        game_board: GameBoard = game_state['game-board']
        player_turn = game_state['player-turn']
        players = game_state['players']
        deck = game_state['deck']
        revealed_goal_cards = game_state['revealed']

        # Extract player info
        player = players[player_turn]
        hand = player['hand']
        path_cards = [card for card in hand if isinstance(card, PathCard)]
        action_cards = [card for card in hand if isinstance(card, ActionCard)]
        card = None

        # Path
        if action == 'path' or action == 'turn':
            x = parts[1]
            y = parts[2]
            path_type = '-'.join(parts[3:])
            for path_card in path_cards:
                if path_card.get_path_type() == path_type:
                    card = path_card
                    break
            # Turn card
            if action == 'turn':
                card.turn_card()
            if GameBoard.can_place_card(x, y, card, game_board.get_board()):
                game_board.add_path_card(x, y, card)
            else:
                raise InvalidMoveException(f"Cannot place path card at {x} {y}")
        else:
            for action_card in action_cards:
                if action_card.get_action() == action:
                    card = action_card
                    break
            # Sabotage
            if action == 'sabotage':
                target = parts[1]
                opponent = players[target]
                opponent['sabotaged'].append('sabotaged')
            elif action == 'mend':
                if len(player['sabotaged']) > 0:
                    player['sabotaged'].pop()
                else:
                    raise InvalidMoveException(f"Player: {player} has not been sabotaged.")
            # Dynamite
            elif action == 'dynamite':
                x = parts[1]
                y = parts[2]
                if game_board.can_remove_card(x, y):
                    game_board.remove_path_card(x, y)
                else:
                    raise InvalidMoveException(f"Cannot remove path card at {x} {y}")
            # Map
            elif action == 'map':
                x = parts[1]
                y = parts[2]
                goal_card = game_board.get_board().get_item_value(x, y)
                if not goal_card.is_special_card():
                    raise InvalidMoveException("Cannot look at a card that is not a goal card.")
                player['seen'].append(((x, y), goal_card.is_gold()))
            # Pass
            elif action == 'pass':
                if parts[1] == 'path':
                    path_type = '-'.join(parts[2:])
                    for path_card in path_cards:
                        if path_card.get_path_type() == path_type:
                            card = path_card
                            break
                else:
                    for action_card in action_cards:
                        if action_card.get_action() == parts[1]:
                            card = action_card
                            break
            else:
                raise InvalidMoveException(f"Action type: {action} not found")

        # Remove and draw card
        if card is None:
            raise InvalidMoveException("Not card found on player.")
        hand.remove(card)
        if deck.cards_remaining() > 0:
            hand.append(deck.draw())

        # Next player
        current_number = int(player_turn[1:])
        next_number = (current_number + 1) % gc.NUMBER_OF_PLAYERS
        next_player_turn = f'P{next_number}'

        # Game state
        new_game_state = {
            'game-board': game_board,
            'player-turn': next_player_turn,
            'players': players,
            'deck': deck,
            'revealed': revealed_goal_cards
        }

        return new_game_state

    def state_transition(self, agent_actuators):
        # No transition possible
        if 'play-card' not in agent_actuators.keys():
            return

        action, position_opponent, card_type = agent_actuators['play-card']

        position = None
        opponent = None
        action = None

        if isinstance(position_opponent, tuple):
            position = position_opponent
        else:
            opponent = position_opponent

        # Place card
        if action == 'path' or action == 'turn':
            action = f'{action}-{position[0]}-{position[0]}-{card_type}'
        elif action == 'mend':
            action = f'{action}'
        elif action == 'dynamite' or action == 'map':
            action = f'{action}-{position[0]}-{position[0]}'
        elif action == 'sabotage':
            action = f'{action}-{opponent}'
        elif action == 'pass':
            if card_type is None:
                f'{action}-{card_type}'
            else:
                f'{action}-path-{card_type}'

        if action is None:
            raise InvalidActionException("Invalid agent actuator action.")

        new_state = GameEnvironment.transition_result(self.get_game_state(), action)

        new_game_board: GameBoard = new_state['game_board']

        # Reveal goal cards
        for goal in gc.GOAL_POSITIONS:
            if GameBoard.can_reach_target(goal, None, gc.START_POSITION, new_game_board.get_board()):
                new_game_board.get_board().get_item_value(goal[0], goal[1]).reveal_card()

        self._game_board = new_game_board
        self._player_turn = new_state['player-turn']
        self._players = new_state['players']
        self._deck = new_state['deck']

    @staticmethod
    def turn(game_state):
        return game_state['player-turn']
