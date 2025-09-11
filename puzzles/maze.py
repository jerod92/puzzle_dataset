# puzzles/maze.py

import random
import math
import numpy as np
from collections import deque
from PIL import Image, ImageDraw
from .base_puzzle import BasePuzzle

class MazePuzzle(BasePuzzle):
    """
    Generates either a rectangular or a circular maze puzzle.
    The goal is to fill the path from the start point to the end point.
    """
    def generate(self):
        maze_type = random.choice(['rectangular', 'circular'])
        
        # Get common colors
        colors = random.sample(self.master_palette, 3)
        start_color, end_color, path_color_hex = colors
        path_color_name = self.color_name_map[path_color_hex]
        description = f"Please fill the path between the dots in {path_color_name}."

        if maze_type == 'rectangular':
            input_image, target_image = self._generate_rectangular_maze(start_color, end_color, path_color_hex)
        else: # circular
            input_image, target_image = self._generate_circular_maze(start_color, end_color, path_color_hex)

        return input_image, target_image, description

    # --- Rectangular Maze Logic ---
    
    def _generate_rectangular_maze(self, start_color, end_color, path_color):
        difficulty = random.choice(['easy', 'medium', 'hard'])
        sizes = {'easy': 11, 'medium': 25, 'hard': 41}
        w, h = sizes[difficulty], sizes[difficulty]
        
        maze = np.ones((h, w), dtype=np.uint8)
        
        # Carve passages using DFS
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

        start_node, end_node = (1, 1), (h - 2, w - 2)
        solution_path = self._solve_rectangular_maze(maze, start_node, end_node)
        
        input_image = self._draw_rectangular_maze(maze, start_node, end_node, start_color, end_color, path_color, solution_path, draw_solution=False)
        target_image = self._draw_rectangular_maze(maze, start_node, end_node, start_color, end_color, path_color, solution_path, draw_solution=True)
        return input_image, target_image

    def _solve_rectangular_maze(self, maze, start_node, end_node):
        h, w = maze.shape
        q = deque([(start_node, [start_node])])
        visited = {start_node}
        while q:
            (y, x), path = q.popleft()
            if (y, x) == end_node: return path
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and maze[ny, nx] == 0 and (ny, nx) not in visited:
                    visited.add((ny, nx))
                    q.append(((ny, nx), path + [(ny, nx)]))
        return []

    def _draw_rectangular_maze(self, maze, start_node, end_node, start_color, end_color, path_color, solution_path, draw_solution):
        h, w = maze.shape
        corridor_width = self.img_size / w
        img = self._create_new_image()
        draw = ImageDraw.Draw(img)

        if draw_solution and solution_path:
            for r, c in solution_path:
                draw.rectangle((c*corridor_width, r*corridor_width, (c+1)*corridor_width, (r+1)*corridor_width), fill=path_color)

        for r in range(h):
            for c in range(w):
                if maze[r, c] == 1:
                    draw.rectangle((c*corridor_width, r*corridor_width, (c+1)*corridor_width, (r+1)*corridor_width), fill=self.line_color)

        radius = corridor_width / 2.2
        for node, color in [(start_node, start_color), (end_node, end_color)]:
            r, c = node
            center_x, center_y = (c + 0.5) * corridor_width, (r + 0.5) * corridor_width
            draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), fill=color)
        return img

    # --- Circular Maze Logic ---

    def _generate_circular_maze(self, start_color, end_color, path_color):
        difficulty = random.choice(['easy', 'medium', 'hard'])
        num_rings = {'easy': 5, 'medium': 10, 'hard': 18}[difficulty]
        
        # Walls: 0 = path, 1 = wall
        radial_walls = np.ones((num_rings, 36), dtype=np.uint8) # Walls between wedges
        circumferential_walls = np.ones((num_rings, 36), dtype=np.uint8) # Walls between rings
        visited = np.zeros((num_rings, 36), dtype=np.uint8)

        def carve(r, c):
            visited[r, c] = 1
            neighbors = [(r, (c+1)%36), (r, (c-1+36)%36), (r+1, c), (r-1, c)]
            random.shuffle(neighbors)
            for nr, nc in neighbors:
                if 0 <= nr < num_rings and not visited[nr, nc]:
                    if r == nr: radial_walls[r, min(c, nc)] = 0
                    else: circumferential_walls[min(r, nr), c] = 0
                    carve(nr, nc)
        carve(0, 0)
        
        start_node, end_node = (0, 0), (num_rings - 1, random.randint(0, 35))
        solution_path = self._solve_circular_maze(radial_walls, circumferential_walls, start_node, end_node)

        input_image = self._draw_circular_maze(num_rings, radial_walls, circumferential_walls, start_node, end_node, start_color, end_color, path_color, solution_path, False)
        target_image = self._draw_circular_maze(num_rings, radial_walls, circumferential_walls, start_node, end_node, start_color, end_color, path_color, solution_path, True)
        return input_image, target_image

    def _solve_circular_maze(self, radial_walls, circumferential_walls, start_node, end_node):
        num_rings, num_wedges = radial_walls.shape
        q = deque([(start_node, [start_node])])
        visited = {start_node}
        while q:
            (r, c), path = q.popleft()
            if (r, c) == end_node: return path
            
            # Potential neighbors
            potential = [((r, (c+1)%num_wedges), radial_walls[r, c]),
                         ((r, (c-1+num_wedges)%num_wedges), radial_walls[r, (c-1+num_wedges)%num_wedges]),
                         ((r+1, c), circumferential_walls[r, c] if r < num_rings-1 else 1),
                         ((r-1, c), circumferential_walls[r-1, c] if r > 0 else 1)]

            for (nr, nc), wall in potential:
                if 0 <= nr < num_rings and (nr, nc) not in visited and wall == 0:
                    visited.add((nr, nc))
                    q.append(((nr, nc), path + [(nr, nc)]))
        return []

    def _draw_circular_maze(self, num_rings, radial_walls, circumferential_walls, start_node, end_node, start_color, end_color, path_color, solution_path, draw_solution):
        img = self._create_new_image()
        draw = ImageDraw.Draw(img)
        center = self.img_size / 2
        ring_height = center / (num_rings + 1)
        
        def cell_to_poly(r, c):
            theta1 = (c / 36) * 360
            theta2 = ((c + 1) / 36) * 360
            r1, r2 = r * ring_height, (r + 1) * ring_height
            
            points = [ (center + r1 * math.cos(math.radians(t)), center + r1 * math.sin(math.radians(t))) for t in np.linspace(theta1, theta2, 10) ]
            points += [ (center + r2 * math.cos(math.radians(t)), center + r2 * math.sin(math.radians(t))) for t in np.linspace(theta2, theta1, 10) ]
            return points

        if draw_solution and solution_path:
            for r, c in solution_path:
                draw.polygon(cell_to_poly(r, c), fill=path_color)
        
        for r in range(num_rings):
            for c in range(36):
                theta = (c / 36) * 360
                r_inner, r_outer = r * ring_height, (r + 1) * ring_height
                
                if circumferential_walls[r, c] == 1 and r < num_rings - 1:
                    draw.arc((center - r_outer, center - r_outer, center + r_outer, center + r_outer), theta, ((c + 1) / 36) * 360, fill=self.line_color, width=2)
                if radial_walls[r, c] == 1:
                    p1 = (center + r_inner * math.cos(math.radians(theta)), center + r_inner * math.sin(math.radians(theta)))
                    p2 = (center + r_outer * math.cos(math.radians(theta)), center + r_outer * math.sin(math.radians(theta)))
                    draw.line([p1, p2], fill=self.line_color, width=2)
        draw.ellipse((center - (num_rings)*ring_height, center - (num_rings)*ring_height, center + (num_rings)*ring_height, center + (num_rings)*ring_height), outline=self.line_color, width=2)

        dot_radius = ring_height / 3
        for node, color in [(start_node, start_color), (end_node, end_color)]:
            r, c = node
            theta = (c + 0.5) / 36 * 360
            radius = (r + 0.5) * ring_height
            cx, cy = center + radius * math.cos(math.radians(theta)), center + radius * math.sin(math.radians(theta))
            draw.ellipse((cx - dot_radius, cy - dot_radius, cx + dot_radius, cy + dot_radius), fill=color)

        return img
