# puzzles/two_d_measuring.py

import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial import ConvexHull
from .base_puzzle import BasePuzzle
from utils.drawing_utils import draw_shape

class TwoDMeasuringPuzzle(BasePuzzle):
    def generate(self):
        task_type = random.choice(['area', 'pouring', 'comparison'])

        if task_type == 'area':
            return self._generate_area_task()
        elif task_type == 'pouring':
            return self._generate_pouring_task()
        else: # comparison
            return self._generate_area_comparison_task()

    # --- Task Generation Methods ---
    def _generate_area_task(self):
        unit_area_pixels = (self.img_size * 0.1)**2
        
        # Generate a random convex polygon
        num_points = random.randint(3, 6)
        points = np.random.rand(num_points, 2) * self.img_size * 0.6 + self.img_size * 0.2
        hull = ConvexHull(points)
        shape_vertices = [tuple(p) for p in points[hull.vertices]]
        
        shape_area_pixels = self._polygon_area(shape_vertices)
        answer = round(shape_area_pixels / unit_area_pixels, 1)
        color = random.choice(self.master_palette)
        
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        self._draw_area_scene(draw_input, shape_vertices, unit_area_pixels, color, "?")
        
        target_image = self._create_new_image()
        draw_target = ImageDraw.Draw(target_image)
        self._draw_area_scene(draw_target, shape_vertices, unit_area_pixels, color, str(answer))
        
        description = "Given the unit area, calculate the area of the shape."
        return input_image, target_image, description

    def _generate_pouring_task(self):
        cup1, liquid1_vol = self._create_cup(pos='left')
        cup2, liquid2_vol = self._create_cup(pos='right', filled=False)
        
        pour_ratio = random.choice([0.25, 0.5, 0.75, 1.0])
        pour_amount = liquid1_vol * pour_ratio
        
        final_vol1 = liquid1_vol - pour_amount
        final_vol2 = liquid2_vol + pour_amount
        
        source_side = 'left'
        dest_side = 'right'
        
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        self._draw_cup(draw_input, cup1, liquid1_vol)
        self._draw_cup(draw_input, cup2, liquid2_vol)

        target_image = self._create_new_image()
        draw_target = ImageDraw.Draw(target_image)
        self._draw_cup(draw_target, cup1, final_vol1)
        self._draw_cup(draw_target, cup2, final_vol2)
        
        prompt_ratio = f"{int(pour_ratio*100)}%" if pour_ratio != 1.0 else "all"
        description = f"Pour {prompt_ratio} of the liquid from the {source_side} cup into the {dest_side} cup."
        return input_image, target_image, description

    def _generate_area_comparison_task(self):
        num_shapes = random.randint(2, 4)
        mode = random.choice(['greatest', 'least'])
        target_color_hex, target_color_name = random.choice(list(self.color_name_map.items()))
        
        shapes = []
        for i in range(num_shapes):
            shape_type = random.choice(['circle', 'square', 'triangle', 'diamond', 'star', 'hexagon'])
            size = self.img_size * random.uniform(0.1, 0.25)
            # Position shapes in a grid
            px = (i % 2) * 0.5 * self.img_size + 0.25 * self.img_size
            py = (i // 2) * 0.5 * self.img_size + 0.25 * self.img_size
            
            # Estimate area based on size for simple shapes
            if shape_type in ['circle', 'square', 'diamond', 'hexagon']: area = size**2
            else: area = size**2 / 2 # Approx for triangle/star
            
            shapes.append({
                'type': shape_type, 'pos': (px, py), 'size': size,
                'color': random.choice(self.master_palette), 'area': area
            })
            
        # Find the target shape
        target_shape = min(shapes, key=lambda s: s['area']) if mode == 'least' else max(shapes, key=lambda s: s['area'])
        
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        for s in shapes:
            draw_shape(draw_input, s['type'], s['pos'], s['size'], s['color'])
            
        target_image = self._create_new_image()
        draw_target = ImageDraw.Draw(target_image)
        for s in shapes:
            color = target_color_hex if s == target_shape else s['color']
            draw_shape(draw_target, s['type'], s['pos'], s['size'], color)
            
        description = f"Change the color of the shape with the {mode} area to {target_color_name}."
        return input_image, target_image, description

    # --- Drawing and Helper Methods ---
    def _polygon_area(self, vertices):
        x, y = zip(*vertices)
        return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    def _draw_area_scene(self, draw, vertices, unit_area, color, answer_text):
        unit_side = math.sqrt(unit_area)
        draw.rectangle((10, 10, 10 + unit_side, 10 + unit_side), outline=self.line_color, fill=self.line_color+'40')
        draw.text((15 + unit_side, 10), "1 unit²", fill=self.line_color, anchor="la")
        
        box_size = self.img_size * 0.2
        box_coords = (self.img_size - box_size - 10, 10, self.img_size - 10, 10 + box_size * 0.5)
        draw.rectangle(box_coords, outline=self.line_color, width=2)
        font = ImageFont.load_default(size=int(box_size * 0.3))
        draw.text((box_coords[0] + (box_coords[2]-box_coords[0])/2, box_coords[1] + (box_coords[3]-box_coords[1])/2), 
                  answer_text, fill=self.line_color, font=font, anchor="mm")
        
        draw.polygon(vertices, fill=color)

    def _create_cup(self, pos, filled=True):
        cup_h = self.img_size * random.uniform(0.4, 0.7)
        top_w = self.img_size * random.uniform(0.15, 0.3)
        bottom_w = top_w * random.uniform(0.5, 1.0)
        
        center_x = self.img_size * 0.25 if pos == 'left' else self.img_size * 0.75
        bottom_y = self.img_size * 0.85
        
        p1 = (center_x - top_w/2, bottom_y - cup_h)
        p2 = (center_x + top_w/2, bottom_y - cup_h)
        p3 = (center_x + bottom_w/2, bottom_y)
        p4 = (center_x - bottom_w/2, bottom_y)
        
        cup = {'vertices': [p1, p2, p3, p4], 'h': cup_h, 'top_w': top_w, 'bottom_w': bottom_w, 'y_bottom': bottom_y}
        
        fill_ratio = random.uniform(0.3, 0.8) if filled else 0
        volume = (top_w + bottom_w) / 2 * cup_h # Trapezoid area
        return cup, volume * fill_ratio

    def _draw_cup(self, draw, cup, volume):
        draw.polygon(cup['vertices'], outline=self.line_color, width=4)
        if volume < 1e-3: return

        # Calculate liquid level (height h) from volume (area A) for a trapezoid
        # A = h * (b + (h/H)*(a-b)/2 + b) -> solve quadratic for h
        H, a, b = cup['h'], cup['top_w'], cup['bottom_w']
        # Simplified linear interpolation for height
        max_vol = (a+b)/2*H
        fill_ratio = volume / max_vol
        liquid_h = H * fill_ratio
        
        y_top = cup['y_bottom'] - H
        y_level = cup['y_bottom'] - liquid_h
        
        # Interpolate width at liquid level
        interp_w = b + (y_level - y_top) / H * (a - b)
        
        center_x = (cup['vertices'][0][0] + cup['vertices'][1][0]) / 2
        liquid_verts = [
            (center_x - interp_w/2, y_level),
            (center_x + interp_w/2, y_level),
            cup['vertices'][2],
            cup['vertices'][3]
        ]
        draw.polygon(liquid_verts, fill='#428bcaA0')
