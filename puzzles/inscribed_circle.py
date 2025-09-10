# puzzles/inscribed_circle.py

import random
import numpy as np
from PIL import ImageDraw
from .base_puzzle import BasePuzzle

class InscribedCirclePuzzle(BasePuzzle):
    def generate(self):
        shape_type = random.choice(['square', 'triangle'])
        color_hex, color_name = random.choice(list(self.color_name_map.items()))

        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)

        if shape_type == 'square':
            side = random.randint(self.img_size // 3, self.img_size // 1.5)
            cx, cy = self.img_size / 2, self.img_size / 2
            x0, y0 = cx - side / 2, cy - side / 2
            x1, y1 = cx + side / 2, cy + side / 2
            
            draw_input.rectangle((x0, y0, x1, y1), outline=self.line_color, width=4)
            
            radius = side / 2
            center = (cx, cy)

        else: # Triangle
            padding = self.img_size * 0.2
            p1 = (random.uniform(padding, self.img_size - padding), random.uniform(padding, self.img_size - padding))
            p2 = (random.uniform(padding, self.img_size - padding), random.uniform(padding, self.img_size - padding))
            p3 = (random.uniform(padding, self.img_size - padding), random.uniform(padding, self.img_size - padding))
            
            draw_input.polygon([p1, p2, p3], outline=self.line_color, width=4)
            
            # Calculate incenter and inradius
            a = np.linalg.norm(np.array(p2) - np.array(p3))
            b = np.linalg.norm(np.array(p1) - np.array(p3))
            c = np.linalg.norm(np.array(p1) - np.array(p2))
            perimeter = a + b + c
            
            ix = (a * p1[0] + b * p2[0] + c * p3[0]) / perimeter
            iy = (a * p1[1] + b * p2[1] + c * p3[1]) / perimeter
            center = (ix, iy)
            
            s = perimeter / 2
            area = np.sqrt(s * (s - a) * (s - b) * (s - c))
            radius = area / s

        target_image = input_image.copy()
        draw_target = ImageDraw.Draw(target_image)
        
        cx, cy = center
        draw_target.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color_hex)
        
        description = f"Draw a {color_name} circle inscribed in the {shape_type}."
        return input_image, target_image, description
