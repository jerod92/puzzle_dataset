# puzzles/tangent_line.py

import random
import math
import numpy as np
from PIL import ImageDraw
from .base_puzzle import BasePuzzle
from utils.drawing_utils import rotate_points

class TangentLinePuzzle(BasePuzzle):
    """
    Generates a puzzle requiring drawing a tangent or normal line to a randomly rotated conic section.
    """
    def generate(self):
        task_type = random.choice(['tangent', 'normal'])
        conic_type = random.choice(['circle', 'ellipse', 'parabola', 'hyperbola'])
        
        draw_params, point, tangent_slope = self._get_conic_data(conic_type)
        
        color_hex, color_name = random.choice(list(self.color_name_map.items()))

        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        self._draw_conic(draw_input, conic_type, draw_params)
        
        point_radius = 8
        draw_input.ellipse((point[0] - point_radius, point[1] - point_radius, point[0] + point_radius, point[1] + point_radius), fill='red')

        target_image = input_image.copy()
        draw_target = ImageDraw.Draw(target_image)

        if task_type == 'tangent':
            final_slope = tangent_slope
        else: # normal
            if tangent_slope is None: final_slope = 0
            elif abs(tangent_slope) < 1e-6: final_slope = None
            else: final_slope = -1 / tangent_slope
        
        line_points = self._get_extended_line_points(point, final_slope)
        if line_points:
            draw_target.line(line_points, fill=color_hex, width=4)

        description = f"Draw a {color_name} {task_type} line to the curve at the marked point."
        return input_image, target_image, description

    def _get_conic_data(self, conic_type):
        cx, cy = self.img_size / 2, self.img_size / 2
        
        if conic_type == 'circle':
            radius = random.uniform(self.img_size * 0.15, self.img_size * 0.35)
            h, k = cx + random.uniform(-self.img_size*0.1, self.img_size*0.1), cy + random.uniform(-self.img_size*0.1, self.img_size*0.1)
            angle = random.uniform(0, 2 * math.pi)
            px, py = h + radius * math.cos(angle), k + radius * math.sin(angle)
            m_tangent = -(px - h) / (py - k) if abs(py - k) > 1e-6 else None
            draw_params = (h - radius, k - radius, h + radius, k + radius)
            return draw_params, (px, py), m_tangent

        rotation_angle = random.uniform(-60, 60)
        
        if conic_type == 'ellipse':
            rx, ry = random.uniform(self.img_size*0.2, self.img_size*0.4), random.uniform(self.img_size*0.1, self.img_size*0.3)
            if rx == ry: ry *= 0.5
            
            t = random.uniform(0, 2 * math.pi)
            px_unrot, py_unrot = cx + rx * math.cos(t), cy + ry * math.sin(t)
            m_unrot = -(px_unrot - cx) * (ry**2) / ((py_unrot - cy) * (rx**2)) if abs(py_unrot - cy) > 1e-6 else None

            t_range = np.linspace(0, 2 * math.pi, 200)
            points_unrot = [(cx + rx * math.cos(val), cy + ry * math.sin(val)) for val in t_range]
            
        elif conic_type == 'parabola':
            h, k = cx, cy
            a = random.uniform(0.005, 0.02) * random.choice([-1, 1])
            x_offset = random.uniform(-self.img_size * 0.25, self.img_size * 0.25)
            px_unrot, py_unrot = h + x_offset, k + a * x_offset**2
            m_unrot = 2 * a * (px_unrot - h)
            
            x_range = np.linspace(-self.img_size / 1.5, self.img_size / 1.5, 200)
            points_unrot = [(h + val, k + a * val**2) for val in x_range]

        elif conic_type == 'hyperbola':
            h, k = cx, cy
            a = random.uniform(self.img_size * 0.1, self.img_size * 0.2)
            b = random.uniform(self.img_size * 0.1, self.img_size * 0.2)
            
            t = random.uniform(-1.5, 1.5)
            branch = random.choice([-1, 1])
            px_unrot = h + branch * a * np.cosh(t)
            py_unrot = k + b * np.sinh(t)
            m_unrot = (b**2 * (px_unrot - h)) / (a**2 * (py_unrot - k)) if abs(py_unrot - k) > 1e-6 else None

            t_range = np.linspace(-2.5, 2.5, 100)
            points_right = [(h + a * np.cosh(t_val), k + b * np.sinh(t_val)) for t_val in t_range]
            points_left = [(h - a * np.cosh(t_val), k + b * np.sinh(t_val)) for t_val in t_range]
            points_unrot = (points_left, points_right)

        # Rotate the points and calculate the new tangent slope
        point_rot = rotate_points([(px_unrot, py_unrot)], (cx, cy), rotation_angle)[0]
        
        if m_unrot is None: # Vertical tangent
            angle_unrot = math.pi / 2
        else:
            angle_unrot = math.atan(m_unrot)
        
        angle_rot = angle_unrot + math.radians(rotation_angle)
        m_rot = math.tan(angle_rot)
        if abs(math.cos(angle_rot)) < 1e-6: m_rot = None # Handle new vertical tangent
        
        return points_unrot, point_rot, m_rot, rotation_angle

    def _get_conic_data(self, conic_type):
        """Modified dispatcher to handle rotation."""
        cx, cy = self.img_size / 2, self.img_size / 2
        
        if conic_type == 'circle':
            # ... (Circle logic is unchanged as it's rotationally symmetric)
            radius = random.uniform(self.img_size * 0.15, self.img_size * 0.35)
            h, k = cx + random.uniform(-self.img_size*0.1, self.img_size*0.1), cy + random.uniform(-self.img_size*0.1, self.img_size*0.1)
            angle = random.uniform(0, 2 * math.pi)
            px, py = h + radius * math.cos(angle), k + radius * math.sin(angle)
            m_tangent = -(px - h) / (py - k) if abs(py - k) > 1e-6 else None
            draw_params = (h - radius, k - radius, h + radius, k + radius)
            return draw_params, (px, py), m_tangent

        # --- Logic for shapes that can be rotated ---
        rotation_angle = random.uniform(-50, 50)
        
        if conic_type == 'ellipse':
            rx, ry = random.uniform(self.img_size*0.2, self.img_size*0.4), random.uniform(self.img_size*0.1, self.img_size*0.3)
            if abs(rx - ry) < self.img_size*0.05: ry *= 0.5 # Ensure it's not too circular
            t = random.uniform(0, 2 * math.pi)
            px_unrot, py_unrot = cx + rx * math.cos(t), cy + ry * math.sin(t)
            m_unrot = -(px_unrot - cx) * (ry**2) / ((py_unrot - cy) * (rx**2)) if abs(py_unrot - cy) > 1e-6 else None
            t_range = np.linspace(0, 2 * math.pi, 200)
            points_unrot = [(cx + rx * math.cos(val), cy + ry * math.sin(val)) for val in t_range]
            
        elif conic_type == 'parabola':
            a = random.uniform(0.005, 0.02) * random.choice([-1, 1])
            x_offset = random.uniform(-self.img_size * 0.25, self.img_size * 0.25)
            px_unrot, py_unrot = cx + x_offset, cy + a * x_offset**2
            m_unrot = 2 * a * (px_unrot - cx)
            x_range = np.linspace(-self.img_size / 1.5, self.img_size / 1.5, 200)
            points_unrot = [(cx + val, cy + a * val**2) for val in x_range]

        elif conic_type == 'hyperbola':
            a = random.uniform(self.img_size * 0.1, self.img_size * 0.2)
            b = random.uniform(self.img_size * 0.1, self.img_size * 0.2)
            t = random.uniform(-1.5, 1.5)
            branch = random.choice([-1, 1])
            px_unrot, py_unrot = cx + branch * a * np.cosh(t), cy + b * np.sinh(t)
            m_unrot = (b**2 * (px_unrot - cx)) / (a**2 * (py_unrot - cy)) if abs(py_unrot - cy) > 1e-6 else None
            t_range = np.linspace(-2.5, 2.5, 100)
            points_right = [(cx + a * np.cosh(t_val), cy + b * np.sinh(t_val)) for t_val in t_range]
            points_left = [(cx - a * np.cosh(t_val), cy + b * np.sinh(t_val)) for t_val in t_range]
            points_unrot = (points_left, points_right)

        # Rotate the points and calculate the new tangent slope
        point_rot = rotate_points([(px_unrot, py_unrot)], (cx, cy), rotation_angle)[0]
        
        if m_unrot is None: angle_unrot = math.pi / 2
        else: angle_unrot = math.atan(m_unrot)
        
        angle_rot = angle_unrot + math.radians(rotation_angle)
        m_rot = math.tan(angle_rot)
        if abs(math.cos(angle_rot)) < 1e-6: m_rot = None
        
        draw_params = (points_unrot, rotation_angle)
        return draw_params, point_rot, m_rot

    def _draw_conic(self, draw, conic_type, params):
        cx, cy = self.img_size / 2, self.img_size / 2
        if conic_type == 'circle':
            draw.ellipse(params, outline=self.line_color, width=4)
            return

        points_unrot, rotation_angle = params
        if conic_type == 'hyperbola':
            points_left, points_right = points_unrot
            draw.line(rotate_points(points_left, (cx, cy), rotation_angle), fill=self.line_color, width=4, joint="curve")
            draw.line(rotate_points(points_right, (cx, cy), rotation_angle), fill=self.line_color, width=4, joint="curve")
        else:
            draw.line(rotate_points(points_unrot, (cx, cy), rotation_angle), fill=self.line_color, width=4, joint="curve")

    def _get_extended_line_points(self, point, slope):
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
