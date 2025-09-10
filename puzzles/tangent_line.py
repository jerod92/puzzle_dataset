# puzzles/tangent_line.py

import random
import math
import numpy as np
from PIL import ImageDraw
from .base_puzzle import BasePuzzle

class TangentLinePuzzle(BasePuzzle):
    def generate(self):
        img_center_x, img_center_y = self.img_size / 2, self.img_size / 2
        
        # Define a circle
        radius = random.randint(self.img_size // 6, self.img_size // 3)
        circle_center_x = img_center_x + random.randint(-self.img_size // 10, self.img_size // 10)
        circle_center_y = img_center_y + random.randint(-self.img_size // 10, self.img_size // 10)

        # Pick a random point on the circle
        angle = random.uniform(0, 2 * math.pi)
        point_x = circle_center_x + radius * math.cos(angle)
        point_y = circle_center_y + radius * math.sin(angle)
        
        # Get a color for the line
        color_hex, color_name = random.choice(list(self.color_name_map.items()))

        # --- Create Input Image ---
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        
        # Draw the circle
        draw_input.ellipse(
            (circle_center_x - radius, circle_center_y - radius, circle_center_x + radius, circle_center_y + radius),
            outline=self.line_color, width=4
        )
        
        # Draw the point on the circle
        point_radius = 8
        draw_input.ellipse(
            (point_x - point_radius, point_y - point_radius, point_x + point_radius, point_y + point_radius),
            fill='red'
        )

        # --- Create Target Image ---
        target_image = input_image.copy()
        draw_target = ImageDraw.Draw(target_image)

        # Calculate and draw the tangent line
        # The slope of the radius is (point_y - circle_center_y) / (point_x - circle_center_x)
        # The slope of the tangent is the negative reciprocal.
        if abs(point_x - circle_center_x) < 1e-6: # Vertical radius -> horizontal tangent
            p1 = (0, point_y)
            p2 = (self.img_size, point_y)
        else:
            m_radius = (point_y - circle_center_y) / (point_x - circle_center_x)
            if abs(m_radius) < 1e-6: # Horizontal radius -> vertical tangent
                p1 = (point_x, 0)
                p2 = (point_x, self.img_size)
            else:
                m_tangent = -1 / m_radius
                # y - y1 = m(x - x1) -> y = mx - mx1 + y1
                b = -m_tangent * point_x + point_y
                # Find intersections with image boundaries
                p1 = (0, b)
                p2 = (self.img_size, m_tangent * self.img_size + b)
        
        draw_target.line([p1, p2], fill=color_hex, width=4)

        description = f"Draw a {color_name} line tangent to the curve at the marked point."
        return input_image, target_image, description
