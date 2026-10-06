from mazegenerator.mazegenerator import MazeGenerator
import random
from typing import List, Tuple,  cast


class Level:
    def __init__(
        self,
        id: int,
        width: int,
        height: int,
        points_per_pacgum: int,
        points_per_super_pacgum: int,
        points_per_ghost: int,
        max_time: int,
        seed: int
    ) -> None:
        """Store the level settings and generate its maze."""
        self.id = id
        self.width = width
        self.height = height
        self.points_per_pacgum = points_per_pacgum
        self.points_per_super_pacgum = points_per_super_pacgum
        self.points_per_ghost = points_per_ghost
        self.max_time = max_time
        self.seed = seed
        self.maze = self.generate(width, height)
        self.supergums: List[Tuple[int, int]] = []
        self.gums: List[Tuple[int, int]] = []
        self.start_time: int | None = None
        self.key: Tuple[int, int] | None = None
        self.collected_score = 0

    def generate(self, width: int, height: int) -> List[List[int]]:
        """Build the maze grid from the level size and seed."""
        maze = MazeGenerator((width, height), False, seed=self.seed)
        return cast(List[List[int]], maze.maze)

    def generate_gums(self) -> None:
        """Place super gums, gums and a random key cell."""
        self.supergums = [
            (x, y) for x in [0, self.width - 1] for y in [0, self.height - 1]
        ]
        self.gums = list(
            {
                (x, y)
                for x in range(self.width)
                for y in range(self.height)
                if self.maze[y][x] < 15 and (x, y) not in self.supergums
            }
        )
        self.key = random.choice(self.gums)
        self.gums.remove(self.key)
