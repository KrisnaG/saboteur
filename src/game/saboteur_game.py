import pygame
import constant.game_constants as gc

class SaboteurGame:
    def __init__(self, players, environment):
        self._agents = {}
        
        for index, player in enumerate(players):
            assert type(player).__name__ == 'SaboteurPlayer', f"Player: {player} must be an instance of the class SaboteurPlayer"
            self._agents[f'P{index}'] = player
        
        assert type(environment).__name__ == 'SaboteurEnvironment', "environment must be an instance of a subclass of the class SaboteurEnvironment"
        self._environment = environment
        
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
        pass


    def _draw_board(self):
        # Clear the background
        self._display.fill(gc.BLACK)
        
        game_state = self._environment.get_game_state()
        game_board = game_state['game-board']
        
        for row in range(len(game_board)):
            for col in range(len(game_board[row])):
                card = game_board[row][col]
                x_coord = col * gc.CARD_WIDTH
                y_coord = row * gc.CARD_HEIGHT
                
                # Draw a card rectangle
                pygame.draw.rect(self._display, gc.CARD_COLOUR, (x_coord, y_coord, gc.CARD_WIDTH, gc.CARD_HEIGHT))
                
                # Draw card content (assuming card has a __str__ method)
                card_text = str(card)
                font = pygame.font.Font(None, gc.FONT_SIZE)
                text_surface = font.render(card_text, True, gc.WHITE)
                text_rect = text_surface.get_rect(center=(x_coord + gc.CARD_WIDTH // 2, y_coord + gc.CARD_HEIGHT // 2))
                
                # Blit card text onto the card rectangle
                self._display.blit(text_surface, text_rect)
        
        # Update the display
        pygame.display.update()


    def _draw_frame(self):
        self._draw_board()


    def wait_for_user_input(self):
        pass

        
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