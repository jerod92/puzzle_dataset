# puzzles/graph.py
import random
import math
import numpy as np
from PIL import ImageDraw, ImageFont
from .base_puzzle import BasePuzzle

class GraphPuzzle(BasePuzzle):
    def generate(self):
        input_image = self._create_new_image()
        draw = ImageDraw.Draw(input_image)
        
        padding = {'top': 70, 'bottom': 40, 'left': 40, 'right': 40}
        
        # Draw grid and axes
        origin, x_scale, y_scale = self._draw_grid(draw, padding)

        # Generate equation
        equation_func, equation_str = self._generate_equation()
        
        # Choose a color for the plot
        color_hex, color_name = random.choice(list(self.color_name_map.items()))
        
        # Draw the equation text on the image
        try:
            eq_font = ImageFont.load_default(size=30)
        except AttributeError:
            eq_font = ImageFont.load_default()
        draw.text((self.img_size/2, padding['top']/2), equation_str, fill=self.line_color, font=eq_font, anchor='mm')
        
        # Create target image by plotting the function
        target_image = input_image.copy()
        draw_target = ImageDraw.Draw(target_image)
        
        self._plot_function(draw_target, equation_func, origin, x_scale, y_scale, color_hex)
        
        description = f"Please plot the equation in {color_name}."
        
        return input_image, target_image, description

    def _draw_grid(self, draw, padding):
        w, h = self.img_size, self.img_size
        axis_range = (-5, 5)
        num_ticks = axis_range[1] - axis_range[0]
        
        graph_width = w - padding['left'] - padding['right']
        graph_height = h - padding['top'] - padding['bottom']

        origin = (padding['left'] + graph_width / 2, padding['top'] + graph_height / 2)
        x_scale = graph_width / num_ticks
        y_scale = graph_height / num_ticks

        # Draw gridlines
        for i in range(num_ticks + 1):
            x = padding['left'] + i * x_scale
            y = padding['top'] + i * y_scale
            draw.line([(x, padding['top']), (x, h - padding['bottom'])], fill='#e0e0e0', width=1)
            draw.line([(padding['left'], y), (w - padding['right'], y)], fill='#e0e0e0', width=1)
        
        # Draw main axes
        draw.line([(padding['left'], origin[1]), (w - padding['right'], origin[1])], fill=self.line_color, width=2)
        draw.line([(origin[0], padding['top']), (origin[0], h - padding['bottom'])], fill=self.line_color, width=2)
        
        # Draw ticks and labels
        try:
            font = ImageFont.load_default(size=15)
        except AttributeError:
            font = ImageFont.load_default()
            
        for i in range(axis_range[0], axis_range[1] + 1):
            if i == 0: continue
            x_pos = origin[0] + i * x_scale
            y_pos = origin[1] - i * y_scale
            draw.line([(x_pos, origin[1] - 5), (x_pos, origin[1] + 5)], fill=self.line_color, width=1)
            draw.text((x_pos, origin[1] + 8), str(i), fill=self.line_color, font=font, anchor='mt')
            draw.line([(origin[0] - 5, y_pos), (origin[0] + 5, y_pos)], fill=self.line_color, width=1)
            draw.text((origin[0] - 8, y_pos), str(i), fill=self.line_color, font=font, anchor='rm')
            
        return origin, x_scale, y_scale

    def _generate_equation(self):
        eq_type = random.choice(['linear', 'quadratic', 'cubic', 'sine'])
        
        def get_random_coeff():
            return round(random.uniform(0.1, 3.0), 2) * random.choice([-1, 1])

        def format_const(val):
            if val == 0: return ""
            val = round(val, 2)
            return f" + {val}" if val > 0 else f" - {abs(val)}"
        
        if eq_type == 'linear':
            m = get_random_coeff()
            c = random.randint(-4, 4)
            f = lambda x: m * x + c
            m_str = "x" if m == 1.0 else "-x" if m == -1.0 else f"{m}x"
            s = f"y = {m_str}{format_const(c)}"

        elif eq_type in ['quadratic', 'cubic']:
            a = get_random_coeff()
            h = random.randint(-3, 3)
            k = random.randint(-3, 3)
            power = 2 if eq_type == 'quadratic' else 3
            f = lambda x: a * (x - h)**power + k
            a_str = "" if a == 1.0 else "-" if a == -1.0 else str(a)
            h_str = f"x^{power}" if h == 0 else f"(x {'-' if h > 0 else '+'} {abs(h)})^{power}"
            s = f"y = {a_str}{h_str}{format_const(k)}"
        
        else: # Sine
            a = round(random.uniform(0.1, 3.0), 2)
            b = random.choice([1, 2])
            k = random.randint(-3, 3)
            f = lambda x: a * math.sin(b * x) + k
            a_str = "" if a == 1.0 else str(a)
            b_str = "x" if b == 1 else f"{b}x"
            s = f"y = {a_str}sin({b_str}){format_const(k)}"
            
        return f, s

    def _plot_function(self, draw, func, origin, x_scale, y_scale, color):
        axis_range = (-5, 5)
        points = []
        for x_val in np.linspace(axis_range[0], axis_range[1], 200):
            y_val = func(x_val)
            if axis_range[0] <= y_val <= axis_range[1]:
                screen_x = origin[0] + x_val * x_scale
                screen_y = origin[1] - y_val * y_scale
                points.append((screen_x, screen_y))
        
        if len(points) > 1:
            draw.line(points, fill=color, width=3)