# puzzles/graph.py

import random
import math
import numpy as np
from PIL import ImageDraw, ImageFont
from .base_puzzle import BasePuzzle

class GraphPuzzle(BasePuzzle):
    """
    A greatly expanded puzzle generator for plotting various mathematical objects.
    
    Can generate and plot:
    - Single points
    - Standard functions (linear, quadratic, cubic)
    - Transcendental functions (sine, tangent, exponential, logarithmic)
    - Parametric curves (circles, ellipses, Lissajous figures)
    """
    def generate(self):
        input_image = self._create_new_image()
        draw = ImageDraw.Draw(input_image)
        
        padding = {'top': 70, 'bottom': 40, 'left': 40, 'right': 40}
        axis_range = (-5, 5)
        
        # Draw grid and axes
        origin, x_scale, y_scale = self._draw_grid(draw, padding, axis_range)

        # Generate the data for a random plot type
        plot_type, plot_data, plot_str = self._generate_plot_data(axis_range)
        
        # Choose a color for the plot
        color_hex, color_name = random.choice(list(self.color_name_map.items()))
        
        # Draw the equation/instruction text on the input image
        try:
            eq_font = ImageFont.load_default(size=24)
        except AttributeError:
            eq_font = ImageFont.load_default()
        draw.text((self.img_size/2, padding['top']/2), plot_str, fill=self.line_color, font=eq_font, anchor='mm', align='center')
        
        # Create target image by plotting the item
        target_image = input_image.copy()
        draw_target = ImageDraw.Draw(target_image)
        
        self._plot_item(draw_target, plot_type, plot_data, origin, x_scale, y_scale, axis_range, color_hex)
        
        description = f"Please plot the item in {color_name}."
        
        return input_image, target_image, description

    def _draw_grid(self, draw, padding, axis_range):
        w, h = self.img_size, self.img_size
        num_ticks = axis_range[1] - axis_range[0]
        
        graph_width = w - padding['left'] - padding['right']
        graph_height = h - padding['top'] - padding['bottom']

        origin = (padding['left'] + graph_width / 2, padding['top'] + graph_height / 2)
        x_scale = graph_width / num_ticks
        y_scale = graph_height / num_ticks

        # Draw gridlines and axes
        for i in range(num_ticks + 1):
            x = padding['left'] + i * x_scale
            y = padding['top'] + i * y_scale
            draw.line([(x, padding['top']), (x, h - padding['bottom'])], fill='#e0e0e0', width=1)
            draw.line([(padding['left'], y), (w - padding['right'], y)], fill='#e0e0e0', width=1)
        draw.line([(padding['left'], origin[1]), (w - padding['right'], origin[1])], fill=self.line_color, width=2)
        draw.line([(origin[0], padding['top']), (origin[0], h - padding['bottom'])], fill=self.line_color, width=2)
        
        # Draw ticks and labels
        try: font = ImageFont.load_default(size=15)
        except AttributeError: font = ImageFont.load_default()
            
        for i in range(axis_range[0], axis_range[1] + 1):
            if i == 0: continue
            x_pos, y_pos = origin[0] + i * x_scale, origin[1] - i * y_scale
            draw.line([(x_pos, origin[1] - 5), (x_pos, origin[1] + 5)], fill=self.line_color, width=1)
            draw.text((x_pos, origin[1] + 8), str(i), fill=self.line_color, font=font, anchor='mt')
            draw.line([(origin[0] - 5, y_pos), (origin[0] + 5, y_pos)], fill=self.line_color, width=1)
            draw.text((origin[0] - 8, y_pos), str(i), fill=self.line_color, font=font, anchor='rm')
            
        return origin, x_scale, y_scale

    def _generate_plot_data(self, axis_range):
        """Dispatcher to generate a random type of plot."""
        plot_types = [
            'point', 'linear', 'quadratic', 'cubic', 'sine', 'tangent',
            'exponential', 'logarithmic', 'parametric_circle'
        ]
        
        plot_type = random.choice(plot_types)

        # --- Helper formatting functions ---
        def format_coeff(val, var=''):
            if val == 1 and var: return ""
            if val == -1 and var: return "-"
            return str(round(val, 2))

        def format_var(val, var):
            if val == 0: return ""
            op = '+' if val > 0 else '-'
            return f" {op} {abs(round(val, 2))}{var}"

        def format_const(val):
            if val == 0: return ""
            op = '+' if val > 0 else '-'
            return f" {op} {abs(round(val, 2))}"

        # --- Generate based on type ---
        if plot_type == 'point':
            x = random.randint(axis_range[0], axis_range[1])
            y = random.randint(axis_range[0], axis_range[1])
            return plot_type, (x, y), f"Plot the point ({x}, {y})"

        if plot_type == 'linear':
            m = round(random.uniform(-3, 3), 1)
            c = random.randint(-4, 4)
            data = lambda x: m * x + c
            m_str = "x" if m == 1 else "-x" if m == -1 else f"{m}x"
            s = f"y = {m_str}{format_const(c)}"
            return plot_type, data, s

        if plot_type in ['quadratic', 'cubic']:
            a = round(random.uniform(0.2, 2.0) * random.choice([-1, 1]), 2)
            h = random.randint(-3, 3)
            k = random.randint(-3, 3)
            power = 2 if plot_type == 'quadratic' else 3
            data = lambda x: a * ((x - h)**power) + k
            a_str = format_coeff(a, '()')
            h_str = f"x^{power}" if h == 0 else f"(x {format_const(-h)})^{power}"
            s = f"y = {a_str}{h_str}{format_const(k)}"
            return plot_type, data, s

        if plot_type in ['sine', 'tangent']:
            a = round(random.uniform(0.5, 3.0), 1)
            b = random.choice([0.5, 1, 2])
            k = random.randint(-2, 2)
            func = math.sin if plot_type == 'sine' else math.tan
            data = lambda x: a * func(b * x) + k
            a_str = format_coeff(a)
            b_str = "x" if b == 1 else f"{b}x"
            s = f"y = {a_str}{plot_type}({b_str}){format_const(k)}"
            return plot_type, data, s

        if plot_type == 'exponential':
            a = round(random.uniform(0.5, 2.0) * random.choice([-1, 1]), 2)
            b = round(random.uniform(1.2, 2.0), 1)
            k = random.randint(-3, 3)
            data = lambda x: a * (b**x) + k
            a_str = format_coeff(a, 'b')
            s = f"y = {a_str}({b})^x{format_const(k)}"
            return plot_type, data, s
        
        if plot_type == 'logarithmic':
            a = round(random.uniform(0.5, 2.0) * random.choice([-1, 1]), 2)
            h = random.randint(-4, 0) # Keep log domain visible
            k = random.randint(-3, 3)
            data = lambda x: a * np.log(x - h) + k if (x - h) > 0 else float('nan')
            a_str = format_coeff(a, 'log')
            s = f"y = {a_str}ln(x {format_const(-h)}){format_const(k)}"
            return plot_type, data, s

        if plot_type == 'parametric_circle':
            a = random.randint(2, 4) # radius for x
            b = a if random.random() > 0.3 else random.randint(2, 4) # radius for y (ellipse)
            x_func = lambda t: a * math.cos(t)
            y_func = lambda t: b * math.sin(t)
            s = f"Parametric Curve:\nx(t) = {a}cos(t)\ny(t) = {b}sin(t)"
            return plot_type, (x_func, y_func), s

        # Default fallback
        return self._generate_plot_data(axis_range)

    def _plot_item(self, draw, plot_type, data, origin, x_scale, y_scale, axis_range, color):
        """Plots any of the generated item types."""
        ox, oy = origin
        
        if plot_type == 'point':
            px, py = data
            radius = 8
            screen_x, screen_y = ox + px * x_scale, oy - py * y_scale
            draw.ellipse((screen_x - radius, screen_y - radius, screen_x + radius, screen_y + radius), fill=color)
            return

        points = []
        if 'parametric' in plot_type:
            x_func, y_func = data
            t_range = np.linspace(0, 2 * math.pi, 400) # Iterate over parameter t
            for t in t_range:
                x_val, y_val = x_func(t), y_func(t)
                if axis_range[0] <= x_val <= axis_range[1] and axis_range[0] <= y_val <= axis_range[1]:
                    points.append((ox + x_val * x_scale, oy - y_val * y_scale))
        else: # Standard y=f(x) functions
            x_range = np.linspace(axis_range[0], axis_range[1], 400) # Iterate over x-axis
            for x_val in x_range:
                try:
                    y_val = data(x_val)
                    if y_val is not None and not np.isnan(y_val) and not np.isinf(y_val):
                         if axis_range[0] <= y_val <= axis_range[1]:
                            points.append((ox + x_val * x_scale, oy - y_val * y_scale))
                         else: # Add a break in the line if it goes off-screen
                             if len(points) > 1:
                                 draw.line(points, fill=color, width=4, joint="curve")
                             points = []
                except (ValueError, ZeroDivisionError):
                    continue
        
        if len(points) > 1:
            draw.line(points, fill=color, width=4, joint="curve")
