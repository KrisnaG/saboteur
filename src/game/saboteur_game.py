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
                (f"Player: {player} must be an instance of the class SaboteurPlayer")
            for _ in range(gc.NUMBER_OF_CARDS):
                player['hand'].append(self._deck.draw())
            self._agents[index] = player

        game_state = self._environment.get_game_state()
        game_board = game_state['game-board']
        self._n_cols = game_board.get_width()
        self._n_rows = game_board.get_height()

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
        # game_state = self._environment.get_game_state()
        # if type(self._environment).is_terminal(game_state):
        #     return
        #
        # cur_colour = type(self._environment).turn(game_state)
        #
        # # SENSE
        # self._agents[cur_colour].sense(self._environment)
        # # THINK
        # actions = self._agents[cur_colour].think()
        # player = 'Yellow' if cur_colour == 'Y' else 'Red'
        # if len(actions) != 0:
        #     self._last_action = "{0} player played the move '{1}'".format(player, actions[0])
        # # ACT
        # self._agents[cur_colour].act(actions, self._environment)
        pass

    def _draw_box(self, row, col, card):
        pass
        # x_coord = col * gc.CARD_WIDTH
        # y_coord = row * gc.CARD_HEIGHT

        # # Draw a card rectangle with white outline
        # pygame.draw.rect(self._display, gc.WHITE, (x_coord, y_coord, gc.CARD_WIDTH, gc.CARD_HEIGHT), 2)

        # if card is not None:
        #     # Draw card content (assuming card has a __str__ method)
        #     card_text = str(card)
        #     font = pygame.font.Font(None, gc.FONT_SIZE)
        #     text_surface = font.render(card_text, True, gc.WHITE)
        #     text_rect = text_surface.get_rect(center=(x_coord + gc.CARD_WIDTH // 2, y_coord + gc.CARD_HEIGHT // 2))

        #     # Blit card text onto the card rectangle
        #     self._display.blit(text_surface, text_rect)

        # game_state = self._environment.get_game_state()
        # game_board = game_state['game-board']
        # x_coord = self._padding_left + x*self._box_size
        # y_coord = self._padding_top + y*self._box_size

        # surface = pygame.Surface((self._box_size,self._box_size))

        # pygame.draw.rect(surface, color, surface.get_rect())
        # self._display.blit(surface, (x_coord, y_coord))

        # cur_checker = game_board.get_item_value(x, y)

        # if cur_checker == 'Y':
        #     checker_color = YELLOW
        # elif cur_checker == 'R':
        #     checker_color = RED
        # elif cur_checker == 'W':
        #     checker_color = GRAY
        # else:
        #     # no checker
        #     checker_color = WHITE
        # checker_surface = pygame.Surface((self._box_size,self._box_size))
        # checker_surface.fill(color)
        # radius = int((self._box_size/2)*0.8)
        # center = int(self._box_size/2)
        # pygame.draw.circle(checker_surface, checker_color, (center, center), radius)
        # self._display.blit(checker_surface, (x_coord, y_coord))

    def _draw_board(self):
        # Clear the background
        self._display.fill(gc.BLACK)

        game_state = self._environment.get_game_state()
        game_board = game_state['game-board']

        font_path = pygame.font.match_font('Arial')
        font = pygame.font.Font(font_path, gc.FONT_SIZE)

        for row in range(self._n_cols):
            for col in range(self._n_rows):
                card = game_board.get_board().get_item_value(row, col)
                x_coord = col * gc.CARD_WIDTH
                y_coord = row * gc.CARD_HEIGHT

                # Draw a card rectangle
                pygame.draw.rect(self._display, gc.WHITE, (x_coord, y_coord, gc.CARD_WIDTH, gc.CARD_HEIGHT), 1)

                if card is not None:
                    card_str = str(card)
                    lines = card_str.split("\n")
                    # Calculate the total height of the multiline text
                    total_height = len(lines) * font.get_height()

                    # Create a surface to render the multiline text
                    text_surface = pygame.Surface((gc.CARD_WIDTH, total_height))

                    # Render each line of text
                    for i, line in enumerate(lines):
                        line_surface = font.render(line, True, gc.WHITE)
                        text_surface.blit(line_surface, (0, i * font.get_height()))

                    # Get the center of the card
                    center_x = x_coord + gc.CARD_WIDTH // 2
                    center_y = y_coord + gc.CARD_HEIGHT // 2

                    # Calculate the position to blit the text surface
                    text_rect = text_surface.get_rect(center=(center_x, center_y))

                    # Blit the multiline text surface onto the display
                    self._display.blit(text_surface, text_rect)

        pygame.display.update()
        # font = pygame.font.Font(None, gc.FONT_SIZE)
        # text_surface = font.render(card_str, True, gc.WHITE)
        # text_rect = text_surface.get_rect(center=(x_coord + gc.CARD_WIDTH // 2, y_coord + gc.CARD_HEIGHT // 2))
        # self._display.blit(text_surface, text_rect)

        # card = game_board.get_board().get_item_value(row, col)
        # self._draw_box(row, col, card)

        # x_coord = col * gc.CARD_WIDTH
        # y_coord = row * gc.CARD_HEIGHT

        # # Draw a card rectangle with white outline
        # pygame.draw.rect(self._display, gc.WHITE, (x_coord, y_coord, gc.CARD_WIDTH, gc.CARD_HEIGHT), 2)

        # if card is not None:
        #     # Draw card content (assuming card has a __str__ method)
        #     card_text = str(card)
        #     font = pygame.font.Font(None, gc.FONT_SIZE)
        #     text_surface = font.render(card_text, True, gc.WHITE)
        #     text_rect = text_surface.get_rect(center=(x_coord + gc.CARD_WIDTH // 2, y_coord + gc.CARD_HEIGHT // 2))

        #     # Blit card text onto the card rectangle
        #     self._display.blit(text_surface, text_rect)

    def _draw_frame(self):
        self._draw_board()

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
