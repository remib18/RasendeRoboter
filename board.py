import pygame
import random
import math
from robot import Robot
from generate_map import Map

class Board:
    def __init__(self, grid_size, cell_size, control_panel_width):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.control_panel_width = control_panel_width
        self.robots = []
        self.selected_robot = None
        self.targets = {}
        self.target_shape = None
        self.target_color = None
        self.robot_images = {}
        self.shape_images = {}
        self.walls = {"Vertical": [], "Horizontal": []}
        self.ai_move = []       # [[direction, color], [direction, color], ...] 
        self.ai_error = False
        self.move_history = []      # [[direction, color], [direction, color], ...] 

    def initialize_board(self, robot_colors):
        pygame.init()
        self.generate_robots_and_target(robot_colors)

        map = Map()
        self.transform_walls_and_targets(map.map_input)

    def reset_parameters(self):
        self.robots = []
        self.target_shape = None
        self.target_color = None
        self.selected_robot = None
        self.walls = {"Vertical": [], "Horizontal": []}
        self.move_history = [] 

    def load_images(self, screen):
        # Scale factor for robot and target icons
        icon_scale_factor = 0.8

        # Load robot images
        for robot in self.robots:
            try:
                # Assuming icons are named ROBOT_COLOR.png 
                self.robot_images[robot.color] = pygame.image.load(f"icon/{robot.color}.png").convert_alpha()
                # Scale the image to 0.9 of the cell size
                new_size = (int(self.cell_size * icon_scale_factor), int(self.cell_size * icon_scale_factor))
                self.robot_images[robot.color] = pygame.transform.scale(self.robot_images[robot.color], new_size)
            except pygame.error as e:
                print(f"Error loading image for robot color {robot.color}: {e}")
        
        # Load shape images
        for target in self.targets:
            try:
                # Assuming icons are named COLOR_SHAPEE.png 
                self.shape_images[target] = pygame.image.load(f"icon/{target}.png").convert_alpha()
                # Scale the image to 0.9 of the cell size
                new_size = (int(self.cell_size * icon_scale_factor), int(self.cell_size * icon_scale_factor))
                self.shape_images[target] = pygame.transform.scale(self.shape_images[target], new_size)
            except pygame.error as e:
                print(f"Error loading image for target {target}: {e}")
        

    def generate_robots_and_target(self, robot_colors):
        # Define the center 4 grids to exclude
        center_x, center_y = self.grid_size // 2, self.grid_size // 2
        excluded_grids = {
            (center_x - 1, center_y - 1),
            (center_x, center_y - 1),
            (center_x - 1, center_y),
            (center_x, center_y)
        }

        for color in robot_colors:
            # Generate robots
            while True:
                rx, ry = random.randint(0, self.grid_size - 1), random.randint(0, self.grid_size - 1)
                if (rx, ry) not in excluded_grids and not any(robot.x == rx and robot.y == ry for robot in self.robots):
                    self.robots.append(Robot(color, rx, ry))
                    break

        # Generate targets
        target_list = ["Circle", "Square", "Triangle", "Hexagon", "Rain"]
        self.target_shape = random.choice(target_list)
        self.target_color = random.choice(robot_colors)

        # self.target_shape = "Rain"
        
        # Set selected robot
        if self.robots:
            for robot in self.robots:
                if self.target_shape == "Rain":
                    robot.target = "Rain"
                    self.selected_robot = robot
                    break
                elif robot.color == self.target_color:
                    robot.target = self.target_color[0] + self.target_shape[0]
                    self.selected_robot = robot
                    break
        

    def transform_walls_and_targets(self, map_input):
        '''
        if map_input:
            for row in map_input:
                print(" ".join(map(str, row)))
        '''

        # Add the vertical walls
        for i in range(0,16):
            for j in range(0,16):
                if map_input[i*2+1][j*2] == 2:
                    self.walls["Vertical"].append((j, i))

        # Add the horizontal walls
        for i in range(0,16):
            #print(map_input[i][:])
            for j in range(0,16):
                if map_input[i*2][j*2+1] == 2:
                    self.walls["Horizontal"].append((j, i))       

        # Place the targets
        for i in range(0,16):
            for j in range(0,16):
                if map_input[i*2+1][j*2+1] != 0:
                    #print(map_input[i*2+1][j*2+1])
                    self.targets[map_input[i*2+1][j*2+1]] = (j, i)
        self.targets.pop("X")
        # Take away X from the targets

        # print(self.walls)
        
        # print(self.targets)

    def draw(self, screen, colors):
        # Draw grid
        for x in range(0, (self.grid_size + 1) * self.cell_size, self.cell_size):
            pygame.draw.line(screen, colors["Gray"], (x, 0), (x, self.grid_size * self.cell_size))
        for y in range(0, (self.grid_size + 1) * self.cell_size, self.cell_size):
            pygame.draw.line(screen, colors["Gray"], (0, y), (self.grid_size * self.cell_size, y))
        
        # Draw walls
        for (x, y) in self.walls["Vertical"]:
            pygame.draw.line(screen, colors["Black"],
                             (x * self.cell_size, y * self.cell_size),
                             (x * self.cell_size, (y + 1) * self.cell_size), 4)
        for (x, y) in self.walls["Horizontal"]:
            pygame.draw.line(screen, colors["Black"],
                             (x * self.cell_size, y * self.cell_size),
                             ((x + 1) * self.cell_size, y * self.cell_size), 4)
        
        # Draw targets (shapes)
        for target, target_position in self.targets.items():
            shape_image = self.shape_images.get(target)
            if shape_image:
                # Get target position
                target_x, target_y = target_position
                # Center the shape icon within the grid cell
                x_offset = (self.cell_size - shape_image.get_width()) // 2
                y_offset = (self.cell_size - shape_image.get_height()) // 2
                # Draw the shape at its target position, centered within the cell
                screen.blit(shape_image, (target_x * self.cell_size + x_offset, target_y * self.cell_size + y_offset))

        # Draw robots
        for robot in self.robots:
            robot_image = self.robot_images.get(robot.color)
            if robot_image:
                # Center the robot icon within the grid cell
                x_offset = (self.cell_size - robot_image.get_width()) // 2
                y_offset = (self.cell_size - robot_image.get_height()) // 2
                # Draw the robot's icon at the correct position, centered within the cell
                screen.blit(robot_image, (robot.x * self.cell_size + x_offset, robot.y * self.cell_size + y_offset))
        
        # Draw information (attempts, robot, target)
        show_robot_image = self.robot_images.get(self.target_color)
        show_target_image = self.shape_images.get(self.target_color[0]+self.target_shape[0])

        if self.target_shape == "Rain":
            show_target_image = self.shape_images.get("Rain")
            if show_target_image:
                # Draw the target's icon at the side bar
                screen.blit(show_target_image, ((self.grid_size + 7.5) * self.cell_size, 8 * self.cell_size))
        
            # Draw label
            font = pygame.font.Font(None, 24)
            label_text = f"Move any robot to the target"
            label_surface = font.render(label_text, True, colors["Black"])  # Render text in black
            label_position = ((self.grid_size + 1.8) * self.cell_size, 8.25 * self.cell_size)  # Position below the arrow
            screen.blit(label_surface, label_position)

        else:    
            if show_robot_image:
                # Draw the robot's icon at the side bar
                screen.blit(show_robot_image, ((self.grid_size + 3) * self.cell_size, 8 * self.cell_size))

            if show_target_image:
                # Draw the target's icon at the side bar
                screen.blit(show_target_image, ((self.grid_size + 6.5) * self.cell_size, 8 * self.cell_size))
            
            # Draw label
            font = pygame.font.Font(None, 24)
            label_text = f"Move            to the target"
            label_surface = font.render(label_text, True, colors["Black"])  # Render text in black
            label_position = ((self.grid_size + 1.8) * self.cell_size, 8.25 * self.cell_size)
            screen.blit(label_surface, label_position)
        
        if self.ai_error:
            # Draw the label
            font = pygame.font.Font(None, 32) 
            label_text = f"AI moving error"
            label_surface = font.render(label_text, True, colors["Black"])  # Render text in black
            label_position = ((self.grid_size + 1.8) * self.cell_size, 10 * self.cell_size)
            screen.blit(label_surface, label_position)
    
    def target_reached_result(self, screen, colors):
        # Draw the label
        font = pygame.font.Font(None, 32) 
        label_text = f"Target reached after {len(self.move_history)} attempts"
        label_surface = font.render(label_text, True, colors["Black"])  # Render text in black
        label_position = ((self.grid_size + 1.8) * self.cell_size, 10 * self.cell_size)  # Position below the arrow
        screen.blit(label_surface, label_position)
            
    def move_robot(self, direction):
        # Ensure a robot is selected
        if self.selected_robot is None:
            return False 

        # Ensure the selected robot not yet reach the target
        if self.selected_robot.reached_target:
            return False

        x, y = self.selected_robot.x, self.selected_robot.y

        while True:
            # Determine next position
            if direction == "Up":
                next_x, next_y = x, y - 1
                if y == 0 or (x, y) in self.walls["Horizontal"]:  # Top boundary or wall above
                    break
            elif direction == "Down":
                next_x, next_y = x, y + 1
                if y == self.grid_size - 1 or (x, y + 1) in self.walls["Horizontal"]:  # Bottom boundary or wall below
                    break
            elif direction == "Left":
                next_x, next_y = x - 1, y
                if x == 0 or (x, y) in self.walls["Vertical"]:  # Left boundary or wall on the left
                    break
            elif direction == "Right":
                next_x, next_y = x + 1, y
                if x == self.grid_size - 1 or (x + 1, y) in self.walls["Vertical"]:  # Right boundary or wall on the right
                    break
            else:
                return False  # Invalid direction

            # Check if another robot blocks the way
            if (next_x, next_y) in [(robot.x, robot.y) for robot in self.robots if robot != self.selected_robot]:
                break

            # Update position
            x, y = next_x, next_y

            # Check if the robot reached its target
            if self.target_shape == "Rain":
                if (x, y) == (self.targets["Rain"]):
                    # print("target reached")
                    self.selected_robot.reached_target = True
                    break
            else:
                if (x, y) == (self.targets[self.target_color[0]+self.target_shape[0]] or self.targets["Rain"]) and self.selected_robot.color == self.target_color:
                    # print("target reached")
                    self.selected_robot.reached_target = True
                    break

        # Final position update
        if (x, y) != (self.selected_robot.x, self.selected_robot.y):
            self.selected_robot.move(x, y)
            self.move_history.append([direction, self.selected_robot.color])
            return True

        return False
