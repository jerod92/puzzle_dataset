# puzzles/maze.py
import random
import numpy as np
from collections import deque
from PIL import Image, ImageDraw
from .base_puzzle import BasePuzzle

class MazePuzzle(BasePuzzle):
    def generate(self):
        difficulty = random.choice(['easy', 'medium', 'hard'])
        sizes = {'easy': 11, 'medium': 25, 'hard': 41}
        w, h = sizes[difficulty], sizes[difficulty]
        corridor_width = self.img_size / w

        colors = random.sample(self.master_palette, 3)
        start_color_hex, end_color_hex, path_color_hex = colors
        path_color_name = self.color_name_map[path_color_hex]

        maze = self._generate_maze_structure(w, h)
        start_node, end_node = (1, 1), (h - 2, w - 2)
        solution_path = self._solve_maze(maze, start_node, end_node)

        input_image = self._draw_maze(maze, w, h, corridor_width, start_node, end_node, start_color_hex, end_color_hex, path_color_hex, solution_path, draw_solution=False)
        target_image = self._draw_maze(maze, w, h, corridor_width, start_node, end_node, start_color_hex, end_color_hex, path_color_hex, solution_path, draw_solution=True)
        description = f"Please fill the path between the dots in {path_color_name}."

        return input_image, target_image, description

    def _generate_maze_structure(self, w, h):
        maze = np.ones((h, w), dtype=np.uint8)
        def carve(cx, cy):
            dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(dirs)
            maze[cy, cx] = 0
            for dx, dy in dirs:
                nx, ny = cx + dx, cy + dy
                if 0 <= ny < h and 0 <= nx < w and maze[ny, nx] == 1:
                    maze[ny - dy//2, nx - dx//2] = 0
                    carve(nx, ny)
        carve(1, 1)
        return maze

    def _solve_maze(self, maze, start_node, end_node):
        h, w = maze.shape
        q = deque([(start_node, [start_node])])
        visited = {start_node}
        while q:
            (y, x), path = q.popleft()
            if (y, x) == end_node:
                return path
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and maze[ny, nx] == 0 and (ny, nx) not in visited:
                    visited.add((ny, nx))
                    q.append(((ny, nx), path + [(ny, nx)]))
        return []

    def _draw_maze(self, maze, w, h, corridor_width, start_node, end_node, start_color, end_color, path_color, solution_path, draw_solution):
        img = self._create_new_image()
        draw = ImageDraw.Draw(img)

        if draw_solution and solution_path:
            for (r, c) in solution_path:
                draw.rectangle(
                    (c * corridor_width, r * corridor_width, (c + 1) * corridor_width, (r + 1) * corridor_width),
                    fill=path_color, outline=None
                )

        for r in range(h):
            for c in range(w):
                if maze[r, c] == 1:
                    draw.rectangle(
                        (c * corridor_width, r * corridor_width, (c + 1) * corridor_width, (r + 1) * corridor_width),
                        fill=self.line_color
                    )

        radius = corridor_width / 2.2
        sy, sx = start_node
        ey, ex = end_node
        draw.ellipse(((sx + 0.5) * corridor_width - radius, (sy + 0.5) * corridor_width - radius, (sx + 0.5) * corridor_width + radius, (sy + 0.5) * corridor_width + radius), fill=start_color)
        draw.ellipse(((ex + 0.5) * corridor_width - radius, (ey + 0.5) * corridor_width - radius, (ex + 0.5) * corridor_width + radius, (ey + 0.5) * corridor_width + radius), fill=end_color)

        return img