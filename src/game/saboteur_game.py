"""
    Author: Krisna Gusti (kgusti@myune.edu.au)
"""

import pygame
import src.constant.game_constants as gc


class SaboteurGame:
    def __init__(self, environment):
        self._agents = {}
        self._deck = environment.get_deck()

        assert type(
            environment).__name__ == 'SaboteurEnvironment', ("environment must be an instance of a subclass of the "
                                                             "class SaboteurEnvironment")
        self._environment = environment

        for index, player in environment.get_players().items():
            assert type(player['player']).__name__ == 'SaboteurPlayer', \
                f"Player: {player} must be an instance of the class SaboteurPlayer"
            for _ in range(gc.NUMBER_OF_CARDS):
                player['hand'].append(self._deck.draw())
            self._agents[index] = player

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
        self._display.fill(gc.BLACK)

    def _play_step(self):
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
        game_state = self._environment.get_game_state()
        game_board = game_state['game-board']

        for row in range(self._n_cols):
            for col in range(self._n_rows):
                card = game_board.get_board().get_item_value(row, col)
                x_coord = col * gc.CARD_WIDTH
                y_coord = row * gc.CARD_HEIGHT

                # Draw a card rectangle
                pygame.draw.rect(self._display, gc.BROWN, (x_coord, y_coord, gc.CARD_WIDTH, gc.CARD_HEIGHT), 1)

                if card is not None:
                    card_type = card.get_image_type()
                    image_path = f"resource/card/{card_type}.png"
                    try:
                        card_image = pygame.image.load(image_path)
                        card_image = pygame.transform.scale(card_image, (gc.CARD_WIDTH, gc.CARD_HEIGHT))
                        if card.is_card_turned():
                            card_image = pygame.transform.rotate(card_image, 180)

                        self._display.blit(card_image, (x_coord, y_coord))
                    except pygame.error:
                        print(f"Image not found: {image_path}")

        pygame.display.update()

    def _draw_text(self, text_message, padding_top, orientation):
        font = pygame.font.SysFont(gc.FONT, gc.FONT_SIZE)
        text_size = font.size(text_message)
        text = font.render(text_message, True, gc.FONT_COLOUR)
        top = (gc.CARD_HEIGHT * gc.BOARD_ROW_SIZE) + padding_top
        if orientation == 'center':
            left = int((gc.DISPLAY_HEIGHT - text_size[0])/2)
        elif orientation == 'left':
            left = 20
        elif orientation == 'right':
            left = gc.DISPLAY_WIDTH - text_size[0]
        else:
            left = 0
        self._display.blit(text, (left, top))

    def _draw_game_over(self):
        pass

    def _draw_frame(self):
        self._display.fill(gc.BLACK)
        self._draw_board()
        self._draw_text(f"Last action: {self._last_action}", 20, 'left')
        if type(self._environment).is_terminal(self._environment.get_game_state()):
            self._draw_game_over()
        else:
            player = type(self._environment).turn(self._environment.get_game_state())
            self._draw_text(f"Player Turn: {player}", 90, 'left')

    def main(self):
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
            pygame.time.delay(2000)
