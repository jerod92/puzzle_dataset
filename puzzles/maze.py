# puzzles/maze.py

import random
import numpy as np
from collections import deque
from PIL import Image, ImageDraw
from .base_puzzle import BasePuzzle

class MazePuzzle(BasePuzzle):
    """
    Generates a rectangular maze puzzle.
    The goal is to fill the path from the start point to the end point.
    """
    def generate(self):
        # --- 1. Setup Parameters ---
        difficulty = random.choice(['easy', 'medium', 'hard'])
        sizes = {'easy': 11, 'medium': 25, 'hard': 41}
        w, h = sizes[difficulty], sizes[difficulty]
        
        colors = random.sample(self.master_palette, 3)
        start_color, end_color, path_color_hex = colors
        path_color_name = self.color_name_map[path_color_hex]
        description = f"Please fill the path between the dots in {path_color_name}."

        # --- 2. Generate and Solve the Maze ---
        maze_grid = self._generate_maze_grid(w, h)
        start_node, end_node = (1, 1), (h - 2, w - 2)
        solution_path = self._solve_maze(maze_grid, start_node, end_node)

        # --- 3. Draw Input and Target Images ---
        input_image = self._draw_maze(maze_grid, start_node, end_node, start_color, end_color, path_color_hex, solution_path, draw_solution=False)
        target_image = self._draw_maze(maze_grid, start_node, end_node, start_color, end_color, path_color_hex, solution_path, draw_solution=True)

        return input_image, target_image, description

    def _generate_maze_grid(self, w, h):
        """Generates the maze structure using a depth-first search (DFS) algorithm."""
        grid = np.ones((h, w), dtype=np.uint8) # 1 represents a wall

        def carve(cx, cy):
            grid[cy, cx] = 0 # 0 represents a path
            
            # Get neighbors in a random order
            neighbors = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(neighbors)
            
            for dx, dy in neighbors:
                nx, ny = cx + dx, cy + dy
                # Check if the neighbor is within bounds and is an unvisited wall
                if 0 <= ny < h and 0 <= nx < w and grid[ny, nx] == 1:
                    grid[ny - dy // 2, nx - dx // 2] = 0 # Carve path to neighbor
                    carve(nx, ny)
        
        carve(1, 1) # Start carving from the top-left corner
        return grid

    def _solve_maze(self, grid, start_node, end_node):
        """Solves the maze using a breadth-first search (BFS) algorithm."""
        h, w = grid.shape
        queue = deque([(start_node, [start_node])]) # (current_position, path_taken)
        visited = {start_node}

        while queue:
            (r, c), path = queue.popleft()

            if (r, c) == end_node:
                return path # Solution found

            # Check neighbors (Up, Down, Left, Right)
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = r + dr, c + dc
                # Check if neighbor is valid, is a path, and has not been visited
                if 0 <= nr < h and 0 <= nc < w and grid[nr, nc] == 0 and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    new_path = path + [(nr, nc)]
                    queue.append(((nr, nc), new_path))
        return [] # No solution found

    def _draw_maze(self, grid, start_node, end_node, start_color, end_color, path_color, solution_path, draw_solution):
        h, w = grid.shape
        corridor_width = self.img_size / w
        img = self._create_new_image()
        draw = ImageDraw.Draw(img)

        # Draw the solution path first (so walls draw over it)
        if draw_solution and solution_path:
            for r, c in solution_path:
                draw.rectangle((c * corridor_width, r * corridor_width, (c + 1) * corridor_width, (r + 1) * corridor_width), fill=path_color)

        # Draw the maze walls
        for r in range(h):
            for c in range(w):
                if grid[r, c] == 1:
                    draw.rectangle((c * corridor_width, r * corridor_width, (c + 1) * corridor_width, (r + 1) * corridor_width), fill=self.line_color)

        # Draw the start and end points
        dot_radius = corridor_width / 2.2
        for node, color in [(start_node, start_color), (end_node, end_color)]:
            r, c = node
            center_x = (c + 0.5) * corridor_width
            center_y = (r + 0.5) * corridor_width
            draw.ellipse((center_x - dot_radius, center_y - dot_radius, center_x + dot_radius, center_y + dot_radius), fill=color)
        
        return img
