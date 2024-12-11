from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class Coordinate:
    x: int
    y: int

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"({self.x}, {self.y})"


class Color(Enum):
    RED = 0
    GREEN = 1
    BLUE = 2
    YELLOW = 3

    def __str__(self):
        return self.name.lower()


class Shape(Enum):
    CIRCLE = 0
    SQUARE = 1
    TRIANGLE = 2
    STAR = 3

    def __str__(self):
        return self.name.lower()


class MirrorAngle(Enum):
    BACKSLASH = 45
    SLASH = 135

    def __str__(self):
        return self.name.lower()


@dataclass
class GameState:
    board_size: int
    """
    The size of the grid of the game board. (`board_size` x `board_size`)
    """

    walls: List[List[Tuple[bool, bool, bool, bool]]]
    """
    A grid representing each cell of the game board. Each cell has a tuple of 4 booleans representing the walls
    in the following order: (up, right, down, left).
    The grid must have the size of `board_size` x `board_size` and a cell in the grid must be accessible by `walls[x][y]`.
    """

    mirrors: List[List[Tuple[Optional[Color], Optional[MirrorAngle]]]]
    """
    A grid representing each cell of the game board.
    The grid must have the size of `board_size` x `board_size` and a cell in the grid must be accessible by `mirrors[x][y]`.
    If the cell has no mirror, the tuple is (None, None).
    """

    chips: List[List[Tuple[Optional[Color], Optional[Shape]]]]
    """
    A grid representing each cell of the game board.
    The grid must have the size of `board_size` x `board_size` and a cell in the grid must be accessible by `chips[x][y]`.
    If the cell has no chip, the tuple is (None, None).
    """

    pawns: List[Coordinate]
    """
    A list of coordinates representing the pawns in the game.
    The list must be ordered by the color of the pawns in the following order: red, green, blue, yellow.
    Exemple:
    ```py
    [
        Coordinate(0, 0),  // Pawn red is at x=0, y=0
        Coordinate(0, 1),  // Pawn green is at x=0, y=1
        Coordinate(0, 2),  // Pawn blue is at x=0, y=2
        Coordinate(0, 3),  // Pawn yellow is at x=0, y=3
    ]
    ```
    """

    current_target: Tuple[Color, Shape]
    """
    The current target of the game.
    """


class Direction(Enum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3


class GameResolutionInterface(ABC):
    """
    Interface that define how to build resolvers for the game.
    """

    def __init__(self, state: GameState):
        self.state = state

    @abstractmethod
    def resolve(self) -> Optional[List[Tuple[Color, Coordinate]]]:
        """
        Find the best solution to reach the target.
        :return: A list of moves in the format to reach the target. None if no solution is found.
        """
        pass