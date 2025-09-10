# puzzles/color_grid.py

import random
from PIL import ImageDraw
from .base_puzzle import BasePuzzle

class ColorGridPuzzle(BasePuzzle):
    def generate(self):
        rows = random.randint(2, 5)
        cols = random.randint(2, 5)
        
        # Create the color data and the descriptive string
        color_array_names = []
        array_string = "["
        for r in range(rows):
            row_names = [random.choice(list(self.color_name_map.values())) for _ in range(cols)]
            color_array_names.append(row_names)
            array_string += f"[{', '.join(row_names)}]"
            if r < rows - 1:
                array_string += ", "
        array_string += "]"
        
        # --- Create Input Image (Empty Grid) ---
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        self._draw_grid(draw_input, rows, cols)
        
        # --- Create Target Image (Filled Grid) ---
        target_image = self._create_new_image()
        draw_target = ImageDraw.Draw(target_image)
        
        color_hex_map = {v: k for k, v in self.color_name_map.items()}
        cell_w, cell_h = self.img_size / cols, self.img_size / rows
        
        for r in range(rows):
            for c in range(cols):
                color_name = color_array_names[r][c]
                color_hex = color_hex_map.get(color_name, self.line_color)
                draw_target.rectangle(
                    (c * cell_w, r * cell_h, (c + 1) * cell_w, (r + 1) * cell_h),
                    fill=color_hex
                )
        self._draw_grid(draw_target, rows, cols) # Draw grid on top
        
        description = f"Color the grid according to the array: {array_string}"
        return input_image, target_image, description

    def _draw_grid(self, draw, rows, cols):
        for r in range(rows + 1):
            y = r * (self.img_size / rows)
            draw.line((0, y, self.img_size, y), fill=self.line_color, width=2)
        for c in range(cols + 1):
            x = c * (self.img_size / cols)
            draw.line((x, 0, x, self.img_size), fill=self.line_color, width=2)
