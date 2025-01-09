from typing import List, Optional, Tuple
from dataclasses import dataclass
from collections import deque

from utils import Coordinate, Direction, GameState, Color, MirrorAngle, Shape, GameResolutionInterface


@dataclass(frozen=True)
class ResolutionState:
    pawns: List[Coordinate]
    cost: int
    previous_state: Optional["ResolutionState"] = None

    def __lt__(self, other: "ResolutionState") -> bool:
        return self.cost < other.cost

    def get_move_sequence(self) -> List[Tuple[Color, Coordinate]]:
        """
        Reconstruct the sequence of moves from the state chain.
        :return: A list of moves in the format.
        """
        moves = []
        current = self
        while current.previous_state is not None:
            # Find what changed between current and previous state
            for pawn_color, (curr_pos, prev_pos) in enumerate(
                zip(current.pawns, current.previous_state.pawns)
            ):
                if curr_pos != prev_pos:
                    moves.append((Color(pawn_color), curr_pos))
                    break
            current = current.previous_state
        return list(reversed(moves))

    def __str__(self):
        pawn_moved = None

        if self.previous_state:
            for i, (curr_pos, prev_pos) in enumerate(
                zip(self.pawns, self.previous_state.pawns)
            ):
                if curr_pos != prev_pos:
                    pawn_moved = i
                    break

        string = "\n\n"

        if pawn_moved is None:
            string += "Initial state:\n"
        else:
            string += f"Move pawn {get_color_name(Color(pawn_moved))} with a cost of {self.cost}:\n"
        string += "\n".join(
            f"  Pawn {i}: ({pos.x}, {pos.y})" + (" <-" if i == pawn_moved else "")
            for i, pos in enumerate(self.pawns)
        )

        return string


def get_color_name(color_code: Color):
    # Define color names for pawns
    colors = ["red", "green", "blue", "yellow"]
    return colors[color_code.value]


def get_shape(shape_code: Shape):
    # Define shape names
    shapes = ["circle", "square", "triangle", "star"]
    return shapes[shape_code.value]


class BFS(GameResolutionInterface):
    def __init__(self, state: "GameState"):
        super().__init__(state)
        self.state = state
        self.visited_positions = [[coords] for coords in self.state.pawns]

    def compute_choices(
        self, state: "ResolutionState", target_pawn_color: Optional[Color] = None
    ) -> List[Tuple[Color, Coordinate]]:
        """
        Compute all possible moves for the current state.
        :param state: The current state.
        :param target_pawn_color: If provided, only compute moves for this specific pawn.
        :return: A list of all possible moves in the format.
        """
        possible_moves: List[Tuple[Color, Coordinate]] = []
        pawn_colors = (
            [target_pawn_color]
            if target_pawn_color is not None
            else Color(range(len(state.pawns)))
        )

        for pawn_color in pawn_colors:
            for direction in Direction:
                target_coords = self._get_pawn_destination(state, pawn_color, direction)

                # Cond: target_coords != None AND (target_pawn_color != None => target_coords not in visited_positions[pawn_color])
                if target_coords is not None and (
                    target_pawn_color is None
                    or target_coords not in self.visited_positions[pawn_color.value]
                ):
                    possible_moves.append((pawn_color, target_coords))
        return possible_moves

    def resolve(self) -> Optional[List[Tuple[Color, Coordinate]]]:
        """
        Find a solution using a basic breadth-first search.
        :return: A list of moves in the format to reach the target. None if no solution is found.
        """
        # Initialize queue and graph structure
        queue = deque([ResolutionState(pawns=self.state.pawns, cost=0)])
        # Get the target pawn color
        target_pawn_color = self.state.current_target[0]
        # Whether we are using the target pawn or not
        using_target_pawn = True
        # List of explored final states
        explored_states = []

        # Debug
        target_coords = self.get_chip_coordinates(*self.state.current_target)
        pawn_coords = self.state.pawns[target_pawn_color.value]
        print(
            "Target:",
            get_color_name(target_pawn_color),
            get_shape(self.state.current_target[1]),
            f"(at x={target_coords.x}, y={target_coords.y})",
            get_color_name(target_pawn_color),
            "pawn",
            f"(at x={pawn_coords.x}, y={pawn_coords.y})",
        )
        print(f"Starting search with {get_color_name(target_pawn_color)} pawn")

        while queue:
            current_state = queue.popleft()
            loc = current_state.pawns[target_pawn_color.value]
            print(f"\nCurent location: ({loc.x}, {loc.y})")

            # Check if we've reached the target
            if self._is_solution(current_state.pawns):
                print("\t-> Solution found.")
                return current_state.get_move_sequence()

            # Compute all possible moves
            moves = self.compute_choices(
                current_state, target_pawn_color if using_target_pawn else None
            )
            has_valid_moves = False

            if not moves:
                print("\t-> No valid moves for this state.")

            # Try all possible moves
            for pawn_color, target_coords in moves:
                has_valid_moves = True
                print("\t-> Move", get_color_name(pawn_color), "to", target_coords, f"{'(visited)' if loc in self.visited_positions[target_pawn_color.value] else ''}")

                # Create new pawn positions list
                new_pawns = list(current_state.pawns)
                new_pawns[pawn_color.value] = target_coords

                # Track this position as visited for this pawn
                self.visited_positions[pawn_color.value].append(target_coords)

                new_state = ResolutionState(
                    pawns=new_pawns,
                    cost=current_state.cost + 1,
                    previous_state=current_state,
                )

                queue.append(new_state)

            if not has_valid_moves:
                explored_states.append(current_state)

        print("\nNo solution found.")
        return None

    def _is_solution(self, pawns: List[Coordinate]) -> bool:
        """
        Check if the target pawn has reached the target position.
        """
        target_pawn_color = self.state.current_target[0]
        target = self.get_chip_coordinates(*self.state.current_target)
        return pawns[target_pawn_color.value] == target

    def _get_pawn_destination(
        self,
        state: ResolutionState,
        pawn_color: Color,
        direction: Direction,
        from_coords: Optional[Coordinate] = None,
    ) -> Optional[Coordinate]:
        """
        Get the destination coordinates for a pawn based on its direction.
        :param state: The current state.
        :param pawn_color: The color of the pawn.
        :param direction: The direction of the move (Direction enum).
        :param from_coords: A Coordinate to override the current position of the pawn used for mirror moves.
        :return: Target coordinates as a Coordinate or None if move is invalid.
        """
        pawn = state.pawns[pawn_color.value]
        if not pawn:
            return None

        current_coord = from_coords if from_coords else pawn
        x, y = current_coord.x, current_coord.y

        direction_deltas = {
            Direction.UP: (0, -1),
            Direction.RIGHT: (1, 0),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
        }
        dx, dy = direction_deltas[direction]

        # Check if there's a wall in the current cell blocking movement in the current direction
        if self.state.walls[x][y][direction.value]:
            return Coordinate(x=x, y=y)

        # Move the pawn in the current direction until it hits a wall, another pawn or is reflected by a mirror
        while (
            0 <= x + dx < self.state.board_size and 0 <= y + dy < self.state.board_size
        ):
            x += dx
            y += dy

            # Check if the pawn is reflected by a mirror
            mirror = self.state.mirrors[x][y]
            if mirror[0] is not None:
                if pawn_color != mirror[0]:
                    continue
                new_direction = self._get_reflected_direction(direction, mirror[1])
                return self._get_pawn_destination(
                    state, pawn_color, new_direction, Coordinate(x=x, y=y)
                )

            # Check if the pawn is blocked by a wall
            if self.state.walls[x][y][direction.value]:
                return Coordinate(x=x, y=y)

            # Check if the pawn is blocked by another pawn
            if self._is_pawn_at(state, Coordinate(x=x, y=y)):
                return Coordinate(x=x - dx, y=y - dy)

        return Coordinate(x=x, y=y)

    @staticmethod
    def _is_pawn_at(state: ResolutionState, target_coords: Coordinate) -> bool:
        """
        Check if another pawn is at the target coordinates.
        :param target_coords: Coordinates to check.
        :return: True if a pawn is present, False otherwise.
        """
        return any(p == target_coords for p in state.pawns if p is not None)

    @staticmethod
    def _get_reflected_direction(
        direction: Direction, mirror_angle: MirrorAngle
    ) -> Direction:
        """
        Get the new direction based on the mirror's angle.
        :param direction: Current direction of the pawn.
        :param mirror_angle: Angle of the mirror 45 (\) or 135 (/).
        :return: New direction after reflection.
        """
        reflection_map = {
            (Direction.UP, MirrorAngle.BACKSLASH): Direction.LEFT,
            (Direction.UP, MirrorAngle.SLASH): Direction.RIGHT,
            (Direction.RIGHT, MirrorAngle.SLASH): Direction.UP,
            (Direction.RIGHT, MirrorAngle.BACKSLASH): Direction.DOWN,
            (Direction.DOWN, MirrorAngle.BACKSLASH): Direction.RIGHT,
            (Direction.DOWN, MirrorAngle.SLASH): Direction.LEFT,
            (Direction.LEFT, MirrorAngle.BACKSLASH): Direction.UP,
            (Direction.LEFT, MirrorAngle.SLASH): Direction.DOWN,
        }
        if (direction, mirror_angle) not in reflection_map:
            raise ValueError(
                f"Invalid mirror angle or direction, got {direction}, {mirror_angle}"
            )
        return reflection_map[(direction, mirror_angle)]

    def get_chip_coordinates(self, color: Color, chip: Shape) -> Coordinate:
        """
        Get the coordinates of a chip on the board.
        :param color: The color of the chip.
        :param chip: The chip number.
        :return: The coordinates of the chip. (x, y)
        """
        for x, col in enumerate(self.state.chips):
            for y, (c, ch) in enumerate(col):
                if c == color and ch == chip:
                    return Coordinate(x=x, y=y)
        raise ValueError(f"Chip {chip} of color {color} not found on the board.")
