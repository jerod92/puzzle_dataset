# puzzles/tangent_line.py

import random
import math
import numpy as np
from PIL import ImageDraw
from .base_puzzle import BasePuzzle

class TangentLinePuzzle(BasePuzzle):
    """
    Generates a puzzle requiring drawing a tangent or normal line to a conic section.
    
    The puzzle randomly chooses:
    - A conic section (circle, ellipse, parabola, or hyperbola).
    - A task (draw the tangent line or the normal line).
    """
    def generate(self):
        # --- 1. Setup Puzzle Parameters ---
        task_type = random.choice(['tangent', 'normal'])
        conic_type = random.choice(['circle', 'ellipse', 'parabola', 'hyperbola'])
        
        # Get data for the chosen conic section
        draw_params, point, tangent_slope = self._get_conic_data(conic_type)
        px, py = point
        
        # Get a color for the line
        color_hex, color_name = random.choice(list(self.color_name_map.items()))

        # --- 2. Create Input Image ---
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        
        self._draw_conic(draw_input, conic_type, draw_params)
        
        # Draw the point marker
        point_radius = 8
        draw_input.ellipse((px - point_radius, py - point_radius, px + point_radius, py + point_radius), fill='red')

        # --- 3. Create Target Image ---
        target_image = input_image.copy()
        draw_target = ImageDraw.Draw(target_image)

        # Determine the slope of the line to be drawn
        if task_type == 'tangent':
            final_slope = tangent_slope
        else: # normal
            if tangent_slope is None: # Vertical tangent
                final_slope = 0 # Horizontal normal
            elif abs(tangent_slope) < 1e-6: # Horizontal tangent
                final_slope = None # Vertical normal
            else:
                final_slope = -1 / tangent_slope
        
        # Calculate the line's endpoints on the canvas and draw it
        line_points = self._get_extended_line_points(point, final_slope)
        if line_points:
            draw_target.line(line_points, fill=color_hex, width=4)

        description = f"Draw a {color_name} {task_type} line to the curve at the marked point."
        return input_image, target_image, description

    def _get_conic_data(self, conic_type):
        """Dispatcher to generate data for a specific conic type."""
        cx, cy = self.img_size / 2, self.img_size / 2
        
        if conic_type == 'circle':
            radius = random.uniform(self.img_size * 0.15, self.img_size * 0.35)
            h, k = cx + random.uniform(-self.img_size*0.1, self.img_size*0.1), cy + random.uniform(-self.img_size*0.1, self.img_size*0.1)
            angle = random.uniform(0, 2 * math.pi)
            px, py = h + radius * math.cos(angle), k + radius * math.sin(angle)
            m_tangent = -(px - h) / (py - k) if abs(py - k) > 1e-6 else None
            draw_params = (h - radius, k - radius, h + radius, k + radius)
            return draw_params, (px, py), m_tangent

        if conic_type == 'ellipse':
            rx, ry = random.uniform(self.img_size*0.2, self.img_size*0.4), random.uniform(self.img_size*0.1, self.img_size*0.3)
            if rx == ry: ry *= 0.5
            angle = random.uniform(0, 2 * math.pi)
            px, py = cx + rx * math.cos(angle), cy + ry * math.sin(angle)
            m_tangent = -(px - cx) * (ry**2) / ((py - cy) * (rx**2)) if abs(py - cy) > 1e-6 else None
            draw_params = (cx - rx, cy - ry, cx + rx, cy + ry)
            return draw_params, (px, py), m_tangent

        if conic_type == 'parabola':
            h, k = cx + random.uniform(-self.img_size*0.2, self.img_size*0.2), cy + random.uniform(-self.img_size*0.2, self.img_size*0.2)
            a = random.uniform(0.005, 0.02) * random.choice([-1, 1])
            x_offset = random.uniform(-self.img_size * 0.2, self.img_size * 0.2)
            px, py = h + x_offset, a * (h + x_offset - h)**2 + k
            m_tangent = 2 * a * (px - h)
            points = [(h + x_off, a * x_off**2 + k) for x_off in np.linspace(-self.img_size/2, self.img_size/2, 200)]
            draw_params = points
            return draw_params, (px, py), m_tangent

        if conic_type == 'hyperbola':
            h, k = cx, cy
            a = random.uniform(self.img_size * 0.1, self.img_size * 0.2)
            b = random.uniform(self.img_size * 0.1, self.img_size * 0.25)
            
            # Choose a random point on one of the branches
            t = random.uniform(-1.5, 1.5) # Range for cosh/sinh
            branch = random.choice([-1, 1])
            px = h + branch * a * np.cosh(t)
            py = k + b * np.sinh(t)

            # For ((x-h)^2/a^2) - ((y-k)^2/b^2) = 1, slope dy/dx = b^2*(x-h) / a^2*(y-k)
            m_tangent = (b**2 * (px - h)) / (a**2 * (py - k)) if abs(py - k) > 1e-6 else None

            # Generate points for both branches of the hyperbola
            t_range = np.linspace(-2.5, 2.5, 100)
            points_right = [(h + a * np.cosh(t_val), k + b * np.sinh(t_val)) for t_val in t_range]
            points_left = [(h - a * np.cosh(t_val), k + b * np.sinh(t_val)) for t_val in t_range]
            draw_params = (points_left, points_right)
            return draw_params, (px, py), m_tangent
            
        return self._get_conic_data('circle') # Fallback

    def _draw_conic(self, draw, conic_type, params):
        """Draws the given conic section."""
        if conic_type in ['circle', 'ellipse']:
            draw.ellipse(params, outline=self.line_color, width=4)
        elif conic_type == 'parabola':
            draw.line(params, fill=self.line_color, width=4, joint="curve")
        elif conic_type == 'hyperbola':
            points_left, points_right = params
            draw.line(points_left, fill=self.line_color, width=4, joint="curve")
            draw.line(points_right, fill=self.line_color, width=4, joint="curve")

    def _get_extended_line_points(self, point, slope):
        """Calculates the start/end points of a line that extends to the canvas edges."""
        px, py = point
        s = self.img_size

        if slope is None: return [(px, 0), (px, s)]
        if abs(slope) < 1e-6: return [(0, py), (s, py)]
        
        b = py - slope * px
        intersections = []
        if 0 <= (0 - b) / slope <= s: intersections.append(((0 - b) / slope, 0))
        if 0 <= (s - b) / slope <= s: intersections.append(((s - b) / slope, s))
        if 0 <= b <= s: intersections.append((0, b))
        if 0 <= slope * s + b <= s: intersections.append((s, slope * s + b))
        
        unique_points = list(dict.fromkeys(intersections))
        return unique_points[:2] if len(unique_points) >= 2 else []
