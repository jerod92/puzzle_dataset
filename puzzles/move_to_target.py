# puzzles/move_to_target.py

import random
import math
import numpy as np
from PIL import ImageDraw
from .base_puzzle import BasePuzzle
from utils.drawing_utils import draw_shape, rotate_points

class MoveToTargetPuzzle(BasePuzzle):
    """
    Generates a puzzle involving spatial transformation.
    
    Randomly chooses one of two tasks:
    1. Move a shape to a target 'X'.
    2. Mirror a shape across a line of reflection.
    """
    def generate(self):
        task_type = random.choice(['move', 'mirror'])

        if task_type == 'move':
            return self._generate_move_task()
        else: # mirror
            return self._generate_mirror_task()

    def _generate_move_task(self):
        shapes = ['circle', 'triangle', 'square', 'diamond', 'star']
        shape_type = random.choice(shapes)
        color_hex = random.choice(self.master_palette)
        shape_size = self.img_size / 6
        padding = shape_size * 1.5
        
        start_pos = (random.uniform(padding, self.img_size - padding), random.uniform(padding, self.img_size - padding))
        target_pos = (random.uniform(padding, self.img_size - padding), random.uniform(padding, self.img_size - padding))
        
        while np.linalg.norm(np.array(start_pos) - np.array(target_pos)) < shape_size * 2:
            target_pos = (random.uniform(padding, self.img_size - padding), random.uniform(padding, self.img_size - padding))

        # Input image
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        draw_shape(draw_input, shape_type, start_pos, shape_size, color_hex)
        self._draw_x_target(draw_input, target_pos, shape_size / 2)
        
        # Target image
        target_image = self._create_new_image()
        draw_target = ImageDraw.Draw(target_image)
        draw_shape(draw_target, shape_type, target_pos, shape_size, color_hex)

        description = f"Move the {shape_type} to the target 'X'."
        return input_image, target_image, description

    def _generate_mirror_task(self):
        # Use shapes that show reflection clearly
        shapes = ['triangle', 'arrow', 'trapezoid', 'star']
        shape_type = random.choice(shapes)
        color_hex, color_name = random.choice(list(self.color_name_map.items()))
        shape_size = self.img_size / 7
        padding = self.img_size * 0.1
        
        # Define a random line of reflection that crosses the image
        p1 = (random.uniform(0, self.img_size), 0)
        p2 = (random.uniform(0, self.img_size), self.img_size)
        if random.random() > 0.5: # 50% chance of being left-to-right instead
            p1 = (0, random.uniform(0, self.img_size))
            p2 = (self.img_size, random.uniform(0, self.img_size))
            
        # Place the shape on one side of the line
        start_center = (random.uniform(padding, self.img_size - padding), random.uniform(padding, self.img_size - padding))

        # Get the vertices of the original shape
        original_vertices = self._get_shape_vertices(shape_type, start_center, shape_size)
        
        # Reflect each vertex to get the new shape
        reflected_vertices = [self._reflect_point(v, p1, p2) for v in original_vertices]

        # Input image: original shape + line
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        draw_input.line([p1, p2], fill=self.line_color, width=3)
        draw_input.polygon(original_vertices, fill=color_hex)
        
        # Target image: input + reflected shape
        target_image = input_image.copy()
        draw_target = ImageDraw.Draw(target_image)
        draw_target.polygon(reflected_vertices, fill=color_hex)
        
        description = f"Mirror the {color_name} {shape_type} across the line."
        return input_image, target_image, description

    def _draw_x_target(self, draw, center, size):
        cx, cy = center
        draw.line((cx - size, cy - size, cx + size, cy + size), fill=self.line_color, width=5)
        draw.line((cx - size, cy + size, cx + size, cy - size), fill=self.line_color, width=5)

    def _reflect_point(self, point, line_p1, line_p2):
        """Reflects a point across the line defined by line_p1 and line_p2."""
        (x, y) = point
        (x1, y1) = line_p1
        (x2, y2) = line_p2

        # Line equation: ax + by + c = 0
        a = y1 - y2
        b = x2 - x1
        c = -a * x1 - b * y1

        # Formula for reflection
        if a**2 + b**2 == 0: return point # Avoid division by zero for invalid lines
        k = -2 * (a * x + b * y + c) / (a**2 + b**2)
        x_reflected = x + k * a
        y_reflected = y + k * b
        return (x_reflected, y_reflected)
        
    def _get_shape_vertices(self, shape_type, center, size, rotation=0):
        """Generates a list of vertices for a given shape, centered at a point."""
        cx, cy = center
        w, h = size, size
        points = []

        if shape_type == 'triangle':
            points = [(cx, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
        elif shape_type == 'trapezoid':
            points = [(cx - w / 2, cy + h / 2), (cx + w / 2, cy + h / 2), (cx + w / 4, cy - h / 2), (cx - w / 4, cy - h / 2)]
        elif shape_type == 'arrow':
            points = [(cx, cy-h/2), (cx+w/2, cy), (cx+w/4, cy), (cx+w/4, cy+h/2), (cx-w/4, cy+h/2), (cx-w/4, cy), (cx-w/2, cy)]
        elif shape_type == 'star':
            for i in range(10):
                angle = math.pi / 5 * i
                r = w / 2 if i % 2 == 0 else w / 4
                points.append((cx + r * math.sin(angle), cy - r * math.cos(angle)))

        return rotate_points(points, center, rotation)
