# puzzles/line_drawing.py
import random
import numpy as np
from PIL import ImageDraw
from .base_puzzle import BasePuzzle

class LineDrawingPuzzle(BasePuzzle):
    def generate(self):
        padding = 50
        radius = 15
        
        p1 = self._get_random_point(padding)
        p2 = self._get_random_point(padding)
        
        # Ensure points are not too close
        while np.linalg.norm(np.array(p1) - np.array(p2)) < radius * 4:
            p2 = self._get_random_point(padding)

        color_hex, color_name = random.choice(list(self.color_name_map.items()))
        
        # Input image with just dots
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        self._draw_dot(draw_input, p1, radius)
        self._draw_dot(draw_input, p2, radius)

        # Target image with the extended line
        target_image = input_image.copy()
        draw_target = ImageDraw.Draw(target_image)
        
        line_points = self._get_extended_line_points(p1, p2)
        if line_points:
            draw_target.line(line_points, fill=color_hex, width=5)

        description = f"Please draw a {color_name} line through the dots, extending to the edge of the canvas"
        return input_image, target_image, description

    def _get_random_point(self, padding):
        return (
            random.randint(padding, self.img_size - padding),
            random.randint(padding, self.img_size - padding)
        )

    def _draw_dot(self, draw, center, radius):
        draw.ellipse(
            (center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius),
            fill=self.line_color
        )
        
    def _get_extended_line_points(self, p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        s = self.img_size
        intersections = []

        if x2 == x1: # Vertical line
            return [(x1, 0), (x1, s)]

        m = (y2 - y1) / (x2 - x1)
        c = y1 - m * x1

        # Check intersections with all four edges
        # y = mx + c  => x = (y-c)/m
        
        # Top edge (y=0)
        x_top = -c / m
        if 0 <= x_top <= s: intersections.append((x_top, 0))
        
        # Bottom edge (y=s)
        x_bottom = (s - c) / m
        if 0 <= x_bottom <= s: intersections.append((x_bottom, s))
        
        # Left edge (x=0)
        y_left = c
        if 0 <= y_left <= s: intersections.append((0, y_left))
        
        # Right edge (x=s)
        y_right = m * s + c
        if 0 <= y_right <= s: intersections.append((s, y_right))
        
        # Return the first two unique points
        unique_points = list(dict.fromkeys(intersections))
        return unique_points[:2] if len(unique_points) >= 2 else []