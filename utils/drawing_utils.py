# utils/drawing_utils.py
import math
import numpy as np

def rotate_points(points, center, angle):
    """Rotates a list of points around a center by a given angle in degrees."""
    rad = np.deg2rad(angle)
    cx, cy = center
    rotated_points = []
    for x, y in points:
        new_x = cx + (x - cx) * np.cos(rad) - (y - cy) * np.sin(rad)
        new_y = cy + (x - cx) * np.sin(rad) + (y - cy) * np.cos(rad)
        rotated_points.append((new_x, new_y))
    return rotated_points

def draw_shape(draw, shape_type, center, size, color, rotation=0, border_color=None, border_width=5, scale=(1, 1)):
    """A general-purpose function to draw various shapes."""
    cx, cy = center
    w, h = size * scale[0], size * scale[1]

    points = []
    if shape_type == 'circle':
        bbox = [cx - w/2, cy - h/2, cx + w/2, cy + h/2]
        draw.ellipse(bbox, fill=color, outline=border_color, width=border_width if border_color else 0)
        return

    elif shape_type == 'square':
        points = [(cx-w/2, cy-h/2), (cx+w/2, cy-h/2), (cx+w/2, cy+h/2), (cx-w/2, cy+h/2)]
    elif shape_type == 'diamond':
        points = [(cx, cy-h/2), (cx+w/2, cy), (cx, cy+h/2), (cx-w/2, cy)]
    elif shape_type == 'triangle':
        points = [(cx, cy-h/2), (cx+w/2, cy+h/2), (cx-w/2, cy+h/2)]
    elif shape_type == 'hexagon':
        points = [(cx + w/2 * math.cos(math.radians(a)), cy + h/2 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
    elif shape_type == 'trapezoid':
        points = [(cx-w/2, cy+h/2), (cx+w/2, cy+h/2), (cx+w/4, cy-h/2), (cx-w/4, cy-h/2)]
    elif shape_type == 'arrow':
        points = [(cx, cy-h/2), (cx+w/2, cy), (cx+w/4, cy), (cx+w/4, cy+h/2), (cx-w/4, cy+h/2), (cx-w/4, cy), (cx-w/2, cy)]
    elif shape_type == 'star':
        for i in range(10):
            angle = math.pi / 5 * i
            r = w/2 if i % 2 == 0 else w/4
            points.append((cx + r * math.sin(angle), cy - r * math.cos(angle)))

    if points:
        rotated = rotate_points(points, center, rotation)
        draw.polygon(rotated, fill=color, outline=border_color, width=border_width if border_color else 0)