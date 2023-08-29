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

    def _draw_board(self):
        # Clear the background
        self._display.fill(gc.BLACK)

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
                        self._display.blit(card_image, (x_coord, y_coord))
                    except pygame.error:
                        print(f"Image not found: {image_path}")

        pygame.display.update()

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
