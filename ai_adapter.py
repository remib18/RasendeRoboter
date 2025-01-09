from typing import Union, Tuple, Optional, List

from board import Board
from utils import GameState, Color, Shape, Coordinate, Algorithm


# Helper dictionaries for translating between the board and the game state
COLOR_MAP = {
    "Red": Color.RED,
    "Green": Color.GREEN,
    "Blue": Color.BLUE,
    "Yellow": Color.YELLOW
}

SHAPE_MAP = {
    "Circle": Shape.CIRCLE,
    "Square": Shape.SQUARE,
    "Hexagon": Shape.STAR,   # Hexagon -> Star
    "Triangle": Shape.TRIANGLE
}

CHIP_MAP = {
    "BC": (Color.BLUE, Shape.CIRCLE),
    "BS": (Color.BLUE, Shape.SQUARE),
    "BH": (Color.BLUE, Shape.STAR),
    "BT": (Color.BLUE, Shape.TRIANGLE),
    "GC": (Color.GREEN, Shape.CIRCLE),
    "GS": (Color.GREEN, Shape.SQUARE),
    "GH": (Color.GREEN, Shape.STAR),
    "GT": (Color.GREEN, Shape.TRIANGLE),
    "RC": (Color.RED, Shape.CIRCLE),
    "RS": (Color.RED, Shape.SQUARE),
    "RH": (Color.RED, Shape.STAR),
    "RT": (Color.RED, Shape.TRIANGLE),
    "YC": (Color.YELLOW, Shape.CIRCLE),
    "YS": (Color.YELLOW, Shape.SQUARE),
    "YH": (Color.YELLOW, Shape.STAR),
    "YT": (Color.YELLOW, Shape.TRIANGLE),
}


class AiAdapter:
    def __init__(self, board: 'Board', algorithm: 'Algorithm'):
        self.board = board
        self.algorithm = algorithm
        self.moves: Optional[List[Tuple[Color, Coordinate]]] = None
        self.found_solution: Optional[bool] = None

    def resolve(self):
        """
        Sends the board to the chosen algorithm (BFS/A*) to resolve the game,
        storing the moves needed to reach the target.
        """
        state = self._convert_board_to_game_state()
        resolver = self._get_resolver(state)
        res = resolver.resolve()
        self.moves = res
        if res is None:
            self.found_solution = False
        else:
            self.found_solution = True


    def _get_resolver(self, state: GameState):
        """
        Returns the appropriate resolver (BFS or A*) based on self.algorithm.
        """
        if self.algorithm == Algorithm.BFS:
            from solving_bfs import BFS
            return BFS(state)
        elif self.algorithm == Algorithm.A_STAR:
            from solving_a_star import AStar
            return AStar(state)
        else:
            raise ValueError(f"Unsupported algorithm: {self.algorithm}")

    def get_converted_moves(self) -> List[List[str]]:
        """
        Converts the moves into [[direction, color], ...], for example:
        [
            ["UP", "RED"],
            ["RIGHT", "GREEN"],
            ...
        ]
        :return: List of moves in the format [[direction, color], ...]
        """
        if not self.moves:
            return []

        # Initialize current positions of each robot color
        color_positions = {}
        for robot in self.board.robots:
            color_enum = COLOR_MAP.get(robot.color)
            if color_enum:
                color_positions[color_enum] = Coordinate(robot.x, robot.y)
            else:
                print(f"Unsupported robot color: {robot.color}")

        converted_moves = []
        for (color, new_coord) in self.moves:
            old_coord = color_positions[color]
            dx = new_coord.x - old_coord.x
            dy = new_coord.y - old_coord.y

            if dx < 0:
                direction = "Left"
            elif dx > 0:
                direction = "Right"
            elif dy < 0:
                direction = "Up"
            elif dy > 0:
                direction = "Down"
            else:
                # No movement (rare/not expected)
                continue

            converted_moves.append([direction, color.name])
            color_positions[color] = new_coord

        return converted_moves

    def _convert_board_to_game_state(self) -> GameState:
        """
        Converts the Board into a GameState, including walls, chips, pawns, and current target.
        """
        walls = self._create_walls()
        chips = self._create_chips()
        robots = self._get_robot_positions()
        target = (self._translate_color(), self._translate_shape())

        return GameState(
            board_size=self.board.grid_size,
            walls=walls,
            mirrors=[[(None, None) for _ in range(self.board.grid_size)] for _ in range(self.board.grid_size)],
            chips=chips,
            pawns=robots,
            current_target=target
        )

    def _create_walls(self) -> List[List[Tuple[bool, bool, bool, bool]]]:
        """
        Generates the walls grid for the GameState.
        Each cell is a tuple (up, right, down, left).
        """
        size = self.board.grid_size
        # Initialize all to no walls
        walls = [[(False, False, False, False) for _ in range(size)] for _ in range(size)]

        # Vertical walls
        for (x, y) in self.board.walls['Vertical']:
            up_walls = walls[x - 1][y]
            walls[x - 1][y] = (up_walls[0], True, up_walls[2], up_walls[3])
            down_walls = walls[x][y]
            walls[x][y] = (down_walls[0], down_walls[1], down_walls[2], True)

        # Horizontal walls
        for (x, y) in self.board.walls['Horizontal']:
            left_walls = walls[x][y - 1]
            walls[x][y - 1] = (left_walls[0], left_walls[1], True, left_walls[3])
            right_walls = walls[x][y]
            walls[x][y] = (True, right_walls[1], right_walls[2], right_walls[3])

        # Surrounding walls
        for i in range(size):
            # Top row
            walls[i][0] = (True, walls[i][0][1], walls[i][0][2], walls[i][0][3])
            # Bottom row
            walls[i][size - 1] = (walls[i][size - 1][0], walls[i][size - 1][1], True, walls[i][size - 1][3])
            # Left col
            walls[0][i] = (walls[0][i][0], True, walls[0][i][2], walls[0][i][3])
            # Right col
            walls[size - 1][i] = (walls[size - 1][i][0], walls[size - 1][i][1], walls[size - 1][i][2], True)

        return walls

    def _create_chips(self) -> List[List[Tuple[Optional[Color], Optional[Shape]]]]:
        """
        Creates the chips grid for the GameState based on the board targets.
        Each cell is (Color, Shape) or (None, None).
        """
        size = self.board.grid_size
        chips = [[(None, None) for _ in range(size)] for _ in range(size)]
        for key, (x, y) in self.board.targets.items():
            chips[x][y] = self._translate_key_chip(key)
        return chips

    def _get_robot_positions(self) -> List[Coordinate]:
        """
        Returns a list of the robots' coordinates in the order [RED, GREEN, BLUE, YELLOW].
        """
        # Dictionary to hold which coordinate belongs to which Color
        robots_by_color = {
            Color.RED: None,
            Color.GREEN: None,
            Color.BLUE: None,
            Color.YELLOW: None
        }

        for robot in self.board.robots:
            color_enum = COLOR_MAP.get(robot.color)
            if color_enum is not None:
                robots_by_color[color_enum] = Coordinate(robot.x, robot.y)
            else:
                print(f"Unsupported robot color: {robot.color}")

        # The order in the list must match the enum’s definition: RED, GREEN, BLUE, YELLOW
        return [robots_by_color[color] for color in Color]

    def _translate_key_chip(self, key: str) -> Union[Tuple[Color, Shape], Tuple[None, None]]:
        """
        Translates the key of the chip (like 'BC', 'RS', etc.) to (Color, Shape).
        If no valid mapping is found, returns (None, None).
        """
        return CHIP_MAP.get(key, (None, None))

    def _translate_shape(self) -> Shape:
        """
        Translates self.board.target_shape into one of the Shape enum values.
        """
        shape_enum = SHAPE_MAP.get(self.board.target_shape)
        if shape_enum == "Rain":
            shape_enum = "Rain"
        
        if shape_enum is None:
            raise ValueError(f"Unsupported chip shape: {self.board.target_shape}")
        return shape_enum

    def _translate_color(self) -> Color:
        """
        Translates self.board.target_color into one of the Color enum values.
        """
        color_enum = COLOR_MAP.get(self.board.target_color)
        if color_enum is None:
            raise ValueError(f"Unsupported chip color: {self.board.target_color}")
        return color_enum
