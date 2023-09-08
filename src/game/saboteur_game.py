"""
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""

import pygame
import src.constant.game_constants as gc


class SaboteurGame:
    def __init__(self, environment):
        """
        Initialize the SaboteurGame instance.\n
        Args:
            environment (SaboteurEnvironment): The game environment for this game instance.
        """
        self._agents = {}
        self._deck = environment.get_deck()

        # Check the type of the environment
        assert type(
            environment).__name__ == 'SaboteurEnvironment', ("environment must be an instance of a subclass of the "
                                                             "class SaboteurEnvironment")
        self._environment = environment

        # Initialise player hands and agents
        for index, player in environment.get_players().items():
            assert type(player['player']).__name__ == 'SaboteurPlayer', \
                f"Player: {player} must be an instance of the class SaboteurPlayer"
            for _ in range(gc.NUMBER_OF_CARDS):
                player['hand'].append(self._deck.draw())
            self._agents[index] = player

        # Get game board dimensions
        game_state = self._environment.get_game_state()
        game_board = game_state['game-board']
        self._n_cols = game_board.get_width()
        self._n_rows = game_board.get_height()

        self._last_action = ""

        # Initialise Pygame
        pygame.init()

        # Set up display
        self._display = pygame.display.set_mode((gc.DISPLAY_WIDTH, gc.DISPLAY_HEIGHT))
        pygame.display.set_caption('Saboteur Game')
        self._window_clock = pygame.time.Clock()

        # Call the main loop to start the game
        self.main()

    def _reset_bg(self):
        """
        Reset the background of the game display to black.
        """
        self._display.fill(gc.BLACK)

    def _play_step(self):
        """
        Execute a single step of the game, which includes sensing, thinking, and acting for the current player.
        """
        game_state = self._environment.get_game_state()

        # Game over
        if type(self._environment).is_terminal(game_state):
            return

        current_player = type(self._environment).turn(game_state)

        # SENSE
        self._agents[current_player]['player'].sense(self._environment)
        # THINK
        actions = self._agents[current_player]['player'].think()
        if len(actions) != 0:
            self._last_action = f"{current_player}: {actions[0]}"
        # ACT
        self._agents[current_player]['player'].act(actions, self._environment)

    def _draw_board(self):
        """
        Draw the game board, including the cards and their images, on the Pygame display.
        """
        game_state = self._environment.get_game_state()
        game_board = game_state['game-board']

        # Iterate over rows and columns to draw each card
        for row in range(self._n_cols):
            for col in range(self._n_rows):
                card = game_board.get_board().get_item_value(row, col)
                x_coord = col * gc.CARD_WIDTH
                y_coord = row * gc.CARD_HEIGHT

                # Draw a card rectangle
                pygame.draw.rect(self._display, gc.BROWN, (x_coord, y_coord, gc.CARD_WIDTH, gc.CARD_HEIGHT), 1)

                # Load and display the card's image
                if card is not None:
                    card_type = card.get_image_type()
                    image_path = f"resource/card/{card_type}.png"
                    try:
                        card_image = pygame.image.load(image_path)
                        card_image = pygame.transform.scale(card_image, (gc.CARD_WIDTH, gc.CARD_HEIGHT))
                        # Rotate the card image 180 degrees if the card is turned
                        if card.is_card_turned():
                            card_image = pygame.transform.rotate(card_image, 180)

                        self._display.blit(card_image, (x_coord, y_coord))
                    except pygame.error:
                        print(f"Image not found: {image_path}")

    def _draw_text(self, text_message, padding_top, orientation, colour=gc.FONT_COLOUR):
        """
        Draw a text message on the Pygame display.\n
        Args:
            text_message (str): The text message to be displayed.
            padding_top (int): The padding from the top of the display.
            orientation (str): The orientation of the text message ('center', 'left', 'right', or 'default').
            colour (str): The colour for the text.
        """
        font = pygame.font.SysFont(gc.FONT, gc.FONT_SIZE)
        text_size = font.size(text_message)
        text = font.render(text_message, True, colour)
        top = (gc.CARD_HEIGHT * gc.BOARD_ROW_SIZE) + padding_top
        if orientation == 'center':
            left = int((gc.DISPLAY_HEIGHT - text_size[0]) / 2) + 200
        elif orientation == 'left':
            left = 20
        elif orientation == 'right':
            left = gc.DISPLAY_WIDTH - text_size[0]
        else:
            left = 0
        self._display.blit(text, (left, top))

    def _draw_game_over(self):
        """
        Draw a text message for the winner on the Pygame display.
        """
        winner = type(self._environment).get_winner(self._environment.get_game_state())
        self._draw_text(f"WINNERS: {winner}!", gc.FIRST_LINE, 'left', gc.BLUE)

    def _draw_saboteurs(self):
        """
        Draw a text message for the saboteur players.
        """
        saboteurs = ', '.join([player for player in self._environment.get_players() if
                               self._environment.get_players()[player]['player-type'] == 'saboteur'])
        self._draw_text(f"Saboteurs: {saboteurs}", gc.SECOND_LINE, 'left')

    def _draw_gold_miners(self):
        """
        Draw a text message for the gold mine players.
        """
        gold_miner = ', '.join([player for player in self._environment.get_players() if
                                self._environment.get_players()[player]['player-type'] == 'gold-miner'])
        self._draw_text(f"Gold Miners: {gold_miner}", gc.THIRD_LINE, 'left')

    def _draw_players_cards(self):
        """
        Draw a text messages for all the players cards.
        """
        players = self._environment.get_players()
        line_position = gc.FIRST_LINE
        for index, key in enumerate(players):
            cards = ', '.join(card.get_type() for card in players[key]['hand'])
            if index % 2 == 0:
                self._draw_text(f"{key}: {cards}", line_position, 'center')
            else:
                self._draw_text(f"{key}: {cards}", line_position, 'right')
                line_position += gc.SPACING

    def _draw_sabotaged_players(self):
        """
        Draw a text messages for all sabotaged players.
        """
        sabotaged_players = ', '.join([player for player in self._environment.get_players()['P0']['sabotaged']])
        self._draw_text(f"Sabotaged Players: {sabotaged_players}", gc.SIXTH_LINE, 'left')

    def _draw_announcements(self):
        announcements = ""
        for player, content in [player for player in self._environment.get_game_state()['announcements'].items()]:
            content_str = ", ".join(map(str, content))
            announcements += f"{player}: {content_str} "
        self._draw_text(f"Announcements: {announcements}", gc.SIXTH_LINE, 'right')

    def _draw_frame(self):
        """
        Draw a single frame of the game.
        """
        self._reset_bg()
        self._draw_board()
        self._draw_players_cards()
        if type(self._environment).is_terminal(self._environment.get_game_state()):
            self._draw_game_over()
        else:
            player = type(self._environment).turn(self._environment.get_game_state())
            self._draw_text(f"Player Turn: {player}", gc.FIRST_LINE, 'left')
        self._draw_saboteurs()
        self._draw_gold_miners()
        self._draw_text(f"Last action: {self._last_action}", gc.FIFTH_LINE, 'left')
        self._draw_sabotaged_players()
        self._draw_announcements()

    def main(self):
        """
        Main game loop for running the Saboteur game.
        """
        running = True

        while running:
            self._draw_frame()
            pygame.display.update()

            self._window_clock.tick(1)

            # Event Tasking
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    running = False

            # sense - think - act
            self._play_step()

            pygame.time.delay(500)
