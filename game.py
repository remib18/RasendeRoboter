import pygame
import time 
from board import Board
from ai_player import AIPlayer

class Game:
    def __init__(self, grid_size, cell_size, control_panel_width, robot_list, colors):
        self.board = Board(grid_size, cell_size, control_panel_width)
        self.board.initialize_board(robot_list)
        self.screen = None
        self.clock = None
        self.robot_list = robot_list
        self.general_font = None
        self.colors = colors
        self.running = True
        self.button_rects = {}
        self.end_screen_button_rects = {}
        self.create_buttons()
        self.start_time = time.time()
        self.estimated_move = ""
        self.ai_player = AIPlayer(self.board)
        self.game_over = False

    def create_buttons(self):
        BUTTON_WIDTH = 100
        BUTTON_HEIGHT = 40
        BUTTON_Y = 50

        # Timer position
        timer_width = self.board.control_panel_width // 2
        timer_offset_x = self.board.grid_size * self.board.cell_size + timer_width // 2 - BUTTON_WIDTH // 2

        self.button_rects = {
            "Restart": pygame.Rect(timer_offset_x + 40, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Quit": pygame.Rect(timer_offset_x + BUTTON_WIDTH*2 + 40, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Up": pygame.Rect(self.board.grid_size * self.board.cell_size + self.board.control_panel_width // 2 - BUTTON_WIDTH // 2, 3*BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Down": pygame.Rect(self.board.grid_size * self.board.cell_size + self.board.control_panel_width // 2 - BUTTON_WIDTH // 2, 3*BUTTON_Y + BUTTON_HEIGHT + BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Left": pygame.Rect(self.board.grid_size * self.board.cell_size + self.board.control_panel_width // 2 - BUTTON_WIDTH * 3 // 2, 3*BUTTON_Y + BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Right": pygame.Rect(self.board.grid_size * self.board.cell_size + self.board.control_panel_width // 2 + BUTTON_WIDTH // 2, 3*BUTTON_Y + BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT),
            "AI play": pygame.Rect(self.board.grid_size * self.board.cell_size + self.board.control_panel_width // 2 - BUTTON_WIDTH // 2, self.board.grid_size * self.board.cell_size - 1.5 * BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        }
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_button_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                self.handle_keyboard_input(event)

    def handle_button_click(self, pos):
        # Check if clicked on a button
        for button_name, button_rect in self.button_rects.items():
            if button_rect.collidepoint(pos):
                print(f"{button_name} button clicked")
                self.trigger_action(button_name)
                return  # Exit early if a button was clicked

        # Check if clicked on a robot
        clicked_x, clicked_y = pos[0] // self.board.cell_size, pos[1] // self.board.cell_size
        for robot in self.board.robots:
            if robot.x == clicked_x and robot.y == clicked_y:
                self.change_selected_robot(robot)
                return  # Exit early if a robot was clicked

    def trigger_action(self, button_name):
        if button_name in ["Up", "Down", "Left", "Right"]:
            self.board.move_robot(button_name)
        elif button_name == "AI play":
            '''
            1. Pass the board situation (robot_list, target_list, wall_list, ... into the algorithm)
            2. Get the AI move steps from the algorithm
            3. Pass the AI move steps into the auto-move function 
            '''

            # Fake date for moving the robot
            # Replace this line with the AI movement generation function
            self.board.ai_move = [['Right', 'Red'], ['Down', 'Yellow'], ['Up', 'Green'], ['Left', 'Blue']]

            
            # Call AI player for the auto play (use the move sequence for inputz)
            self.ai_play_turn(self.board.ai_move)
        
        elif button_name == "Restart":
            print("Game Restarted")
            self.board.reset_parameters()
            self.board.initialize_board(self.robot_list)
            self.start_time = time.time()
            self.draw(self.screen, self.general_font)

        elif button_name == "Quit":
            print("Game Exited")
            self.running = False

        #print(self.board.move_history)
    
    def ai_play_turn(self, move_sequence):
        for direction, color in move_sequence:
            # Change selected robot if needed
            if self.board.selected_robot.color != color:
                for robot in self.board.robots:
                    if robot.color == color:
                        self.change_selected_robot(robot)
            
            # Move the robot (break if move is invalid)
            if not self.board.move_robot(direction):
                self.board.ai_error = True
                print("AI moving error")
                break
            else: 
                print("move", direction, self.board.selected_robot.color)
            time.sleep(1)

            # Update the display
            self.screen.fill(self.colors["White"])
            self.draw(self.screen, self.general_font)
            pygame.display.flip()
            self.clock.tick(60)

    def change_selected_robot(self, robot):
        if self.board.selected_robot != robot:
            print(f"Changing selected robot to: {robot.color}")
            self.board.selected_robot = robot
        else:
            print(f"Robot {robot.color} is already selected.")

    def handle_keyboard_input(self, event):
        key_to_direction = {
            pygame.K_UP: "Up",
            pygame.K_DOWN: "Down",
            pygame.K_LEFT: "Left",
            pygame.K_RIGHT: "Right",
        }

        # Check if the key is mapped to a direction
        if event.key in key_to_direction:
            direction = key_to_direction[event.key]
            if self.board.move_robot(direction):
                print(f"Robot {self.board.selected_robot.color} moved {direction}.")
            else:
                print(f"Robot {self.board.selected_robot.color} cannot move {direction}.")
        print(self.board.move_history)

    def draw_buttons(self, screen, general_font):
        for button_name, button_rect in self.button_rects.items():
            if button_name in ["Restart", "Quit", "AI play"]:
                color = self.colors["Gray"]  # Neutral color for game controls
            else:
                color = self.colors[self.board.selected_robot.color] if self.board.selected_robot else self.colors["red"]

            pygame.draw.rect(screen, color, button_rect)
            label = general_font.render(button_name, True, self.colors["White"])
            screen.blit(label, (button_rect.x + 10, button_rect.y + 10))
    
    def draw_timer(self, screen, general_font):
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        timer_text = f"Time: {minutes:02}:{seconds:02}"
        timer_label = general_font.render(timer_text, True, self.colors["Black"])
        timer_x = self.board.grid_size * self.board.cell_size + 20  # Position on the control panel
        timer_y = 10  # Top margin
        screen.blit(timer_label, (timer_x, timer_y))

    def draw(self, screen, general_font):
        self.board.draw(screen, self.colors)
        self.draw_buttons(screen, general_font)
        self.draw_timer(screen, general_font)

    def display_end_screen(self):
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)  # Create an alpha-enabled surface
        overlay.fill((128, 128, 128, 128))  # RGBA: Gray with 50% transparency
        self.screen.blit(overlay, (0, 0))  # Draw the overlay

        # Button dimensions and positions
        BUTTON_WIDTH, BUTTON_HEIGHT = 150, 50
        screen_center_x = self.screen.get_width() // 2
        screen_center_y = self.screen.get_height() // 2
        restart_button_rect = pygame.Rect(screen_center_x - BUTTON_WIDTH - 10, screen_center_y, BUTTON_WIDTH, BUTTON_HEIGHT)
        quit_button_rect = pygame.Rect(screen_center_x + 10, screen_center_y, BUTTON_WIDTH, BUTTON_HEIGHT)

        self.end_screen_button_rects = {
            "Restart": restart_button_rect,
            "Quit": quit_button_rect,
        }

        # Draw buttons
        for button_name, button_rect in self.end_screen_button_rects.items():
            button_overlay = pygame.Surface((BUTTON_WIDTH, BUTTON_HEIGHT), pygame.SRCALPHA)
            button_overlay.fill((128, 128, 128, 255))  # Gray with 80% transparency
            self.screen.blit(button_overlay, button_rect.topleft)

            # Draw button labels
            label = self.general_font.render(button_name, True, self.colors["White"])
            label_rect = label.get_rect(center=button_rect.center)
            self.screen.blit(label, label_rect)

        pygame.display.flip()  # Update the display to show the overlay

    def handle_end_screen_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for button_name, button_rect in self.end_screen_button_rects.items():
                    if button_rect.collidepoint(event.pos):
                        print(f"{button_name} button clicked")
                        if button_name == "Restart":
                            print("Game Restarted")
                            # Clear the gray overlay and reset the game state
                            self.screen.fill(self.colors["White"])
                            self.board.reset_parameters()
                            self.board.initialize_board(self.robot_list)
                            self.start_time = time.time()
                            self.running = True  # Ensure the game loop continues
                            self.draw(self.screen, self.general_font)
                            pygame.display.flip()  # Update the display
                            
                            self.game_over = False  # Reset the game over state
                        elif button_name == "Quit":
                            self.running = False


    def run(self):
        pygame.init()
        self.general_font = pygame.font.Font(None, 30)
        screen_width = self.board.grid_size * self.board.cell_size + self.board.control_panel_width
        screen_height = self.board.grid_size * self.board.cell_size
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        self.board.load_images(self.screen)
        self.clock = pygame.time.Clock()
        self.game_over = False  # Flag to manage the post-target UI
        
        while self.running:
            if self.board.selected_robot.reached_target and not self.game_over:
                print("GAME: target reached")
                self.board.target_reached_result(self.screen, self.colors)
                self.display_end_screen()  # Call the new method for the overlay
                self.game_over = True  # Mark the game as finished

            if not self.game_over:
                # Process events
                self.handle_events()

                # Clear the screen
                self.screen.fill(self.colors["White"])

                # Draw the board and buttons
                self.draw(self.screen, self.general_font)

                # Update the display
                pygame.display.flip()

                # Cap the frame rate
                self.clock.tick(60)
            else:
                # Handle the overlay state for Restart and Quit buttons
                self.handle_end_screen_events()

        pygame.quit()  # Quit Pygame properly after the game ends

if __name__ == "__main__":
    COLORS = {
        "White": (255, 255, 255),
        "Black": (0, 0, 0),
        "Gray": (128, 128, 128),
        "Red": (255, 0, 0),
        "Blue": (0, 0, 255),
        "Green": (0, 255, 0),
        "Yellow": (255, 255, 0),
    }

    ROBOTS = ["Red", "Blue", "Green", "Yellow"]

    GRID_SIZE = 16
    CELL_SIZE = 40
    CONTROL_PANEL_WIDTH = 500
    
    game = Game(GRID_SIZE, CELL_SIZE, CONTROL_PANEL_WIDTH, ROBOTS, COLORS)
    game.run()
