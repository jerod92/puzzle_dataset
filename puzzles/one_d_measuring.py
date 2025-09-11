# puzzles/one_d_measuring.py

import random
import numpy as np
from PIL import ImageDraw, ImageFont
from scipy.special import comb
from .base_puzzle import BasePuzzle

class OneDMeasuringPuzzle(BasePuzzle):
    def generate(self):
        task_type = random.choice(['line', 'curve', 'distance'])
        
        # --- 1. Setup Unit and Answer Box ---
        unit_pixel_length = self.img_size * 0.1
        box_size = self.img_size * 0.2
        
        # --- 2. Generate task-specific data ---
        if task_type == 'line':
            p1 = (random.uniform(0.2*self.img_size, 0.8*self.img_size), random.uniform(0.2*self.img_size, 0.8*self.img_size))
            p2 = (random.uniform(0.2*self.img_size, 0.8*self.img_size), random.uniform(0.2*self.img_size, 0.8*self.img_size))
            draw_data = ('line', (p1, p2))
            length_pixels = np.linalg.norm(np.array(p1) - np.array(p2))
            
        elif task_type == 'curve':
            start = np.array([0.2 * self.img_size, random.uniform(0.3, 0.7) * self.img_size])
            end = np.array([0.8 * self.img_size, random.uniform(0.3, 0.7) * self.img_size])
            ctrl1 = start + np.array([random.uniform(0.1, 0.3) * self.img_size, random.uniform(-0.4, 0.4) * self.img_size])
            ctrl2 = end - np.array([random.uniform(0.1, 0.3) * self.img_size, random.uniform(-0.4, 0.4) * self.img_size])
            points = [tuple(p) for p in [start, ctrl1, ctrl2, end]]
            draw_data = ('curve', points)
            length_pixels = self._bezier_arc_length(points)

        else: # distance
            p1 = (random.uniform(0.2*self.img_size, 0.8*self.img_size), random.uniform(0.2*self.img_size, 0.8*self.img_size))
            p2 = (random.uniform(0.2*self.img_size, 0.8*self.img_size), random.uniform(0.2*self.img_size, 0.8*self.img_size))
            draw_data = ('distance', (p1, p2))
            length_pixels = np.linalg.norm(np.array(p1) - np.array(p2))
            
        answer = round(length_pixels / unit_pixel_length, 1)
        color = random.choice(self.master_palette)
        
        # --- 3. Draw Images ---
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        self._draw_measuring_scene(draw_input, draw_data, unit_pixel_length, box_size, color, "?")
        
        target_image = self._create_new_image()
        draw_target = ImageDraw.Draw(target_image)
        self._draw_measuring_scene(draw_target, draw_data, unit_pixel_length, box_size, color, str(answer))
        
        description = f"Given the unit distance, measure the length of the {self.color_name_map[color]} object."
        return input_image, target_image, description

    def _draw_measuring_scene(self, draw, draw_data, unit_len, box_size, color, answer_text):
        # Draw unit reference
        draw.line([(20, 20), (20 + unit_len, 20)], fill=self.line_color, width=4)
        draw.text((20 + unit_len/2, 30), "1 unit", fill=self.line_color, anchor="mt")

        # Draw answer box
        box_coords = (self.img_size - box_size - 10, 10, self.img_size - 10, 10 + box_size * 0.5)
        draw.rectangle(box_coords, outline=self.line_color, width=2)
        font = ImageFont.load_default(size=int(box_size * 0.3))
        draw.text((box_coords[0] + (box_coords[2]-box_coords[0])/2, box_coords[1] + (box_coords[3]-box_coords[1])/2), 
                  answer_text, fill=self.line_color, font=font, anchor="mm")
        
        # Draw the object to be measured
        obj_type, data = draw_data
        if obj_type == 'line':
            draw.line(data, fill=color, width=5)
        elif obj_type == 'curve':
            # Approximate Bezier with a polyline
            curve_points = [self._bezier_point(data, t) for t in np.linspace(0, 1, 100)]
            draw.line(curve_points, fill=color, width=5, joint="curve")
        elif obj_type == 'distance':
            p1, p2 = data
            rad = 8
            draw.ellipse((p1[0]-rad, p1[1]-rad, p1[0]+rad, p1[1]+rad), fill=color)
            draw.ellipse((p2[0]-rad, p2[1]-rad, p2[0]+rad, p2[1]+rad), fill=color)

    def _bernstein_poly(self, i, n, t):
        return comb(n, i) * (t**i) * ((1 - t)**(n - i))

    def _bezier_point(self, points, t):
        n = len(points) - 1
        return sum(self._bernstein_poly(i, n, t) * np.array(p) for i, p in enumerate(points))

    def _bezier_arc_length(self, points, num_segments=100):
        length = 0.0
        p_prev = self._bezier_point(points, 0)
        for i in range(1, num_segments + 1):
            t = i / num_segments
            p_curr = self._bezier_point(points, t)
            length += np.linalg.norm(p_curr - p_prev)
            p_prev = p_curr
        return length
