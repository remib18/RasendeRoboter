import heapq
from typing import List, Optional, Tuple
from dataclasses import dataclass
from collections import deque
from utils import Coordinate, Direction, GameState, Color, MirrorAngle, Shape

@dataclass(frozen=True)
class ResolutionState:
    pawns: List[Coordinate]# Positions of all pawns
    cost: int 
    heuristic: int  # A* heuristic value
    previous_state: Optional["ResolutionState"] = None

    # Comparison function for the priority queue based on cost + heuristic
    def __lt__(self, other: "ResolutionState") -> bool:
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)

    # Generates the sequence of moves from the current state to the initial state
    def get_move_sequence(self) -> List[Tuple[Color, Coordinate]]:
        moves = []
        current = self
     # Traverse back through previous states to generate the sequence of moves
        while current.previous_state is not None:
            for pawn_color, (curr_pos, prev_pos) in enumerate(
                zip(current.pawns, current.previous_state.pawns)
            ):
                if curr_pos != prev_pos:
                    moves.append((Color(pawn_color), curr_pos))# Record the move of the pawn
                    break
            current = current.previous_state
        return list(reversed(moves)) # Return the sequence in the correct order

    # Custom string representation for debugging and output
    def __str__(self):
        pawn_moved = None

        if self.previous_state:
          # Find the pawn that was moved in this state
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
    
# Helper function to convert color code to its name
def get_color_name(color_code: Color):
    colors = ["red", "green", "blue", "yellow"]
    return colors[color_code.value]

def get_shape(shape_code: Shape):
    shapes = ["circle", "square", "triangle", "star"]
    return shapes[shape_code.value]

# AI player class that will use A* to find the solution
class AIPlayer:
    def __init__(self, state: "GameState"):
        self.name = "AI"
        self.state = state # Current game state
        self.visited_positions = [[coords] for coords in self.state.pawns]

    # Compute the possible moves for a given state
    def compute_choices(self, state: "ResolutionState", target_pawn_color: Optional[Color] = None) -> List[Tuple[Color, Coordinate]]:
        possible_moves: List[Tuple[Color, Coordinate]] = []
        pawn_colors = (
            [target_pawn_color] # If a target pawn is specified, limit to that pawn
            if target_pawn_color is not None
            else Color(range(len(state.pawns))) # Otherwise consider all pawns
        )

         # Loop through all pawns and directions to generate possible moves
        for pawn_color in pawn_colors:
            for direction in Direction:
                target_coords = self._get_pawn_destination(state, pawn_color, direction)
        # Only add the move if it's valid and the pawn hasn't visited this position before
                if target_coords is not None and (
                    target_pawn_color is None
                    or target_coords not in self.visited_positions[pawn_color.value]
                ):
                    possible_moves.append((pawn_color, target_coords))
        return possible_moves

    # Solve the puzzle using A* algorithm
    def solve(self) -> Optional[List[Tuple[Color, Coordinate]]]:
        # Initialize priority queue and set of explored states
        open_list = []
        heapq.heappush(open_list, ResolutionState(pawns=self.state.pawns, cost=0, heuristic=self._calculate_heuristic(self.state.pawns)))
        explored_states = set()

        # Get the target position for the current pawn
        target_coords = self.get_chip_coordinates(*self.state.current_target)
        target_pawn_color = self.state.current_target[0]
        print("Target:", get_color_name(target_pawn_color), get_shape(self.state.current_target[1]), f"(at x={target_coords.x}, y={target_coords.y})")

        # A* loop to find the optimal solution
        while open_list:
            current_state = heapq.heappop(open_list) # Get the state with the lowest cost + heuristic

            # Check if we've reached the target
            if self._is_solution(current_state.pawns):
                return current_state.get_move_sequence()

            # Mark state as visited
            state_tuple = tuple(current_state.pawns)
            if state_tuple in explored_states:
                continue
            explored_states.add(state_tuple)

            # Compute all possible moves
            moves = self.compute_choices(current_state, target_pawn_color)
            has_valid_moves = False

            for pawn_color, target_coords in moves:
                has_valid_moves = True

                new_pawns = list(current_state.pawns)
                new_pawns[pawn_color.value] = target_coords

            # Create a new state with the updated positions and add it to the open list
                new_state = ResolutionState(
                    pawns=new_pawns,
                    cost=current_state.cost + 1,
                    heuristic=self._calculate_heuristic(new_pawns),
                    previous_state=current_state,
                )

                heapq.heappush(open_list, new_state)

            if not has_valid_moves:
                print("No valid moves found at this step.")

        print("No solution found.")
        return None

    def _calculate_heuristic(self, pawns: List[Coordinate]) -> int:
        """
        Calculate the heuristic for the A* algorithm.
        Here, we estimate the distance to the target as the Manhattan distance of the target pawn.
        """
        target_pawn_color = self.state.current_target[0]
        target_coords = self.get_chip_coordinates(*self.state.current_target)
        pawn_coords = pawns[target_pawn_color.value]
        return abs(target_coords.x - pawn_coords.x) + abs(target_coords.y - pawn_coords.y)

    # Check if the current state is a solution (i.e., target pawn is at its destination)
    def _is_solution(self, pawns: List[Coordinate]) -> bool:
        target_pawn_color = self.state.current_target[0]
        target = self.get_chip_coordinates(*self.state.current_target)
        return pawns[target_pawn_color.value] == target
    
    # Get the destination of a pawn based on its direction
    def _get_pawn_destination(self, state: ResolutionState, pawn_color: Color, direction: Direction) -> Optional[Coordinate]:
        pawn = state.pawns[pawn_color.value]
        if not pawn:
            return None

        x, y = pawn.x, pawn.y
        direction_deltas = {
            Direction.UP: (0, -1),
            Direction.RIGHT: (1, 0),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
        }
        dx, dy = direction_deltas[direction]

        # If there's a wall, the pawn can't move
        if self.state.walls[x][y][direction.value]:
            return Coordinate(x=x, y=y)

        # Keep moving in the direction until hitting an obstacle
        while 0 <= x + dx < self.state.board_size and 0 <= y + dy < self.state.board_size:
            x += dx
            y += dy

         # Handle reflections if there are mirrors
            mirror = self.state.mirrors[x][y]
            if mirror[0] is not None:
                if pawn_color != mirror[0]:
                    continue
                new_direction = self._get_reflected_direction(direction, mirror[1])
                return self._get_pawn_destination(state, pawn_color, new_direction, Coordinate(x=x, y=y))

            # If there's a wall or pawn at the new position, stop
            if self.state.walls[x][y][direction.value]:
                return Coordinate(x=x, y=y)

            if self._is_pawn_at(state, Coordinate(x=x, y=y)):
                return Coordinate(x=x - dx, y=y - dy)

        return Coordinate(x=x, y=y)

    # Check if there's a pawn at the target coordinates
    @staticmethod
    def _is_pawn_at(state: ResolutionState, target_coords: Coordinate) -> bool:
        return any(p == target_coords for p in state.pawns if p is not None)

    @staticmethod
    def _get_reflected_direction(direction: Direction, mirror_angle: MirrorAngle) -> Direction:
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
        return reflection_map[(direction, mirror_angle)]

    # Find the coordinates of a specific chip based on color and shape
    def get_chip_coordinates(self, color: Color, chip: Shape) -> Coordinate:
        for x, col in enumerate(self.state.chips):
            for y, (c, ch) in enumerate(col):
                if c == color and ch == chip:
                    return Coordinate(x=x, y=y)
        raise ValueError(f"Chip {chip} of color {color} not found on the board.")


