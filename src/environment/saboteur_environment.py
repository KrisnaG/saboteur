"""
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""

from une_ai.models import GameEnvironment

import src.constant.game_constants as gc
from src.component.card.action_card import ActionCard
from src.component.card.path_card import PathCard
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
        self._sabotaged = []
        self._players_actions = {f'P{i}': [] for i in range(gc.NUMBER_OF_PLAYERS)}
        self._announcements = {f'P{i}': [] for i in range(gc.NUMBER_OF_PLAYERS)}

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
        assert len(self._players) < gc.NUMBER_OF_PLAYERS, \
            f"It is not possible to add more than {gc.NUMBER_OF_PLAYERS} players for this game."

        player_number = len(self._players)
        player_type = "gold-miner"

        if player_number in self._chosen_saboteurs:
            player_type = "saboteur"

        hand, seen = [], []

        self._players[f'P{player_number}'] = {
            'player': player,
            'player-type': player_type,
            'hand': hand,
            'sabotaged': self._sabotaged,
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
            'revealed': self._revealed_goal_cards,
            'players-actions': self._players_actions,
            'announcements': self._announcements
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
        if player not in sabotaged:
            # Path cards
            for y, row in enumerate(game_board.get_board_map()):
                for x, cell in enumerate(row):
                    if cell is None:
                        for path_card in path_cards:
                            # Check card placements
                            if GameBoard.can_place_card(x, y, path_card, game_board.get_board()):
                                legal_actions.append(f'path-{x}-{y}-{path_card.get_path_type()}')

                            # Turn card and check placements
                            turned_card = path_card.copy()
                            turned_card.turn_card()
                            if GameBoard.can_place_card(x, y, turned_card, game_board.get_board()):
                                legal_actions.append(f'turn-{x}-{y}-{path_card.get_path_type()}')
        # Sabotage
        for card in action_cards:
            action = card.get_action()
            if action == 'sabotage':
                for opponent in players:
                    if opponent != turn and opponent not in sabotaged:
                        legal_actions.append(f'sabotage-{opponent}')
                break

        # Mend
        for card in action_cards:
            if card.get_action() == 'mend':
                for player in sabotaged:
                    legal_actions.append(f'mend-{player}')
                break

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
                    legal_actions.append(f'pass-{card.get_action()}')

        return legal_actions

    def get_percepts(self):
        """
        Get percepts or information about the game state for the current player.
        Returns:
              dict: A dictionary containing various percepts.
        """
        game_state = self.get_game_state()
        game_board = game_state['game-board']
        player = game_state['players'][self._player_turn]

        return {
            'game-board-sensor': game_board,
            'turn-taking-indicator': self._player_turn,
            'deck-sensor': self._deck,
            'revealed-sensor': self._revealed_goal_cards,
            'players-actions-sensor': self._players_actions,
            'announcements-sensor': self._announcements,
            'player-sensor': player,
            'player-type-sensor': player['player-type'],
            'hand-sensor': player['hand'],
            'sabotaged-sensor': self._sabotaged,
            'seen-sensor': player['seen'],
        }

    @staticmethod
    def get_winner(game_state):
        """
        Determines whether the game state has a winner.\n
        Args:
            game_state (dict): A dictionary representing the current state of the game.
        Returns:
            str: gold-miner, saboteur or None
        """
        game_board: GameBoard = game_state['game-board']
        deck = game_state['deck']
        players = game_state['players']
        board = game_board.get_board()

        # Gold Miners Win - Gold card is reached
        for goal in gc.GOAL_POSITIONS:
            goal_card = board.get_item_value(goal[0], goal[1])
            if goal_card.is_gold() and goal_card.is_revealed():
                if GameBoard.can_reach_target(gc.START_POSITION, None, goal, board):
                    return "gold-miner"

        # Saboteurs Win - No cards remaining which is equal to no actions remaining
        empty_deck = deck.cards_remaining() <= 0
        empty_player_hands = all(
            player is None or (players[player] is not None and len(players[player]['hand']) <= 0)
            for player in players
        )

        if empty_deck and empty_player_hands:
            return 'saboteur'

        return None

    @staticmethod
    def is_terminal(game_state):
        """
        Determines whether the game state represents a terminal state.\n
        Args:
            game_state (dict): A dictionary representing the current state of the game.
        Returns:
            bool: True if the game state is terminal, False otherwise.
        """
        winner = SaboteurEnvironment.get_winner(game_state)
        return winner is not None

    @staticmethod
    def payoff(game_state, player_name):
        """
        Not implemented here.
        As a gold miner and saboteur have different definition of payoff, it is defined in the program.
        """
        pass

    @staticmethod
    def transition_result(game_state, action_str):
        """
        Transitions a game state from the given action.\n
        Args:
            game_state (dict): A dictionary representing the current state of the game.
            action_str (str): Action to execute on game state.
        Returns:
            dict: The new game state.
        """
        # Extract action
        parts = action_str.split('-')
        action = parts[0]

        if len(parts) <= 1:
            raise InvalidActionException(f"Invalid action: {action_str}.")

        # Extract game state
        game_board: GameBoard = game_state['game-board'].copy()
        player_turn = game_state['player-turn']
        players = game_state['players']
        deck = game_state['deck']
        revealed_goal_cards = game_state['revealed']
        player_actions = game_state['players-actions']
        announcement = game_state['announcements']

        # Extract player info
        player = players[player_turn]
        hand = player['hand']
        path_cards = [card for card in hand if isinstance(card, PathCard)]
        action_cards = [card for card in hand if isinstance(card, ActionCard)]
        card = None
        copied_card = None

        # Path
        if action == 'path' or action == 'turn':
            x = int(parts[1])
            y = int(parts[2])
            path_type = '-'.join(parts[3:])
            for path_card in path_cards:
                if path_card.get_path_type() == path_type:
                    card = path_card
                    copied_card = card.copy()
                    break
            # Turn card
            if action == 'turn':
                copied_card.turn_card()
            if GameBoard.can_place_card(x, y, copied_card, game_board.get_board()):
                game_board.add_path_card(x, y, copied_card)
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
                player['sabotaged'].append(target)
            elif action == 'mend':
                target = parts[1]
                if target in player['sabotaged']:
                    player['sabotaged'].remove(target)
                else:
                    raise InvalidMoveException(f"Player: {target} has not been sabotaged.")
            # Dynamite
            elif action == 'dynamite':
                x = int(parts[1])
                y = int(parts[2])
                if game_board.can_remove_card(x, y):
                    game_board.remove_path_card(x, y)
                else:
                    raise InvalidMoveException(f"Cannot remove path card at {x} {y}")
            # Map
            elif action == 'map':
                x = int(parts[1])
                y = int(parts[2])
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
            'revealed': revealed_goal_cards,
            'players-actions': player_actions,
            'announcements': announcement
        }

        return new_game_state, (card, player_turn)

    def state_transition(self, agent_actuators):
        """
        Transitions the state of the game.
        Args:
            agent_actuators: A agents actuator action.
        """
        # No transition possible
        if 'play-card' not in agent_actuators.keys():
            return

        action, position_player, card_type = agent_actuators['play-card']
        should_draw = agent_actuators['draw-card']

        position = None
        player = None
        action_str = None

        if isinstance(position_player, tuple):
            position = position_player
        else:
            player = position_player

        # Place card
        if action == 'path' or action == 'turn':
            action_str = f'{action}-{position[0]}-{position[1]}-{card_type}'
        elif action == 'mend':
            action_str = f'{action}-{player}'
        elif action == 'dynamite' or action == 'map':
            action_str = f'{action}-{position[0]}-{position[1]}'
        elif action == 'sabotage':
            action_str = f'{action}-{player}'
        elif action == 'pass':
            if card_type is None:
                action_str = f'{action}-{card_type}'
            else:
                action_str = f'{action}-{card_type}'

        if action is None or action_str is None:
            raise InvalidActionException("Invalid agent actuator action.")

        new_state, play = SaboteurEnvironment.transition_result(self.get_game_state(), action_str)

        card, player_turn = play
        player = new_state['players'][player_turn]
        hand = player['hand']
        deck = new_state['deck']

        self._players_actions[player_turn].append(action_str)

        # Announce from map card
        if action == 'map':
            if player['player-type'] == 'gold-miner':
                new_state['announcements'][player_turn] = player['seen']
            elif player['player-type'] == 'saboteur':
                new_state['announcements'][player_turn].append(
                    (random.choice(gc.GOAL_POSITIONS), random.choice([True, False])))

        # Remove and draw card
        if card is None:
            raise InvalidMoveException("No card found on player.")
        hand.remove(card)

        if should_draw and deck.cards_remaining() > 0:
            hand.append(deck.draw())

        new_game_board = new_state['game-board']

        # Reveal goal cards
        for goal in gc.GOAL_POSITIONS:
            card = new_game_board.get_board().get_item_value(goal[0], goal[1])
            if not card.is_revealed():
                if GameBoard.can_reach_target(goal, None, gc.START_POSITION, new_game_board.get_board()):
                    card.reveal_card()
                    self._revealed_goal_cards.append((goal[0], goal[1]))

        self._game_board = new_game_board
        self._player_turn = new_state['player-turn']
        self._players = new_state['players']
        self._deck = new_state['deck']
        self._announcements = new_state['announcements']

    @staticmethod
    def turn(game_state):
        """
        Gets the players turn from the current game state.
        Args:
            game_state (dict): A dictionary representing the current state of the game.
        Returns:
            str: The current players turn.
        """
        return game_state['player-turn']
