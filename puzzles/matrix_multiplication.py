# puzzles/matrix_multiplication.py

import numpy as np
import random
from PIL import ImageDraw, ImageFont
from .base_puzzle import BasePuzzle

class MatrixMultiplicationPuzzle(BasePuzzle):
    def generate(self):
        # --- 1. Generate Matrices ---
        n, m = random.randint(1, 3), random.randint(1, 3)
        i, j = m, random.randint(1, 3) # m must equal i
        
        mat_A = np.random.randint(-9, 10, size=(n, m))
        mat_B = np.random.randint(-9, 10, size=(i, j))
        mat_C = np.dot(mat_A, mat_B)

        # --- 2. Draw Images ---
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        self._draw_equation(draw_input, mat_A, mat_B, None)

        target_image = self._create_new_image()
        draw_target = ImageDraw.Draw(target_image)
        self._draw_equation(draw_target, mat_A, mat_B, mat_C)

        description = "Perform the matrix multiplication and fill in the result."
        return input_image, target_image, description

    def _draw_equation(self, draw, mat_a, mat_b, mat_c):
        try: font = ImageFont.load_default(size=24)
        except: font = ImageFont.load_default()
        
        padding = 20
        total_width = self.img_size - 2 * padding
        
        # Estimate widths to center the equation
        w_a = mat_a.shape[1] * 30 + 20
        w_b = mat_b.shape[1] * 30 + 20
        w_c = mat_c.shape[1] * 30 + 20 if mat_c is not None else 40
        op_width = 30
        
        full_eq_width = w_a + op_width + w_b + op_width + w_c
        start_x = (self.img_size - full_eq_width) / 2
        y_center = self.img_size / 2

        # Draw Matrix A
        self._draw_matrix(draw, mat_a, start_x, y_center, font)
        
        # Draw 'x'
        curr_x = start_x + w_a + op_width / 2
        draw.text((curr_x, y_center), "x", fill=self.line_color, font=font, anchor="mm")
        
        # Draw Matrix B
        curr_x += op_width / 2
        self._draw_matrix(draw, mat_b, curr_x, y_center, font)
        
        # Draw '='
        curr_x += w_b + op_width / 2
        draw.text((curr_x, y_center), "=", fill=self.line_color, font=font, anchor="mm")
        
        # Draw Matrix C or '?'
        curr_x += op_width / 2
        if mat_c is not None:
            self._draw_matrix(draw, mat_c, curr_x, y_center, font)
        else:
            q_font = ImageFont.load_default(size=50)
            draw.text((curr_x + w_c/2, y_center), "?", fill=self.line_color, font=q_font, anchor="mm")

    def _draw_matrix(self, draw, matrix, x_start, y_center, font):
        rows, cols = matrix.shape
        cell_size = 30
        width = cols * cell_size
        height = rows * cell_size
        
        y_start = y_center - height / 2
        
        # Brackets
        draw.line([(x_start, y_start), (x_start + 5, y_start)], fill=self.line_color, width=3)
        draw.line([(x_start, y_start), (x_start, y_start + height)], fill=self.line_color, width=3)
        draw.line([(x_start, y_start + height), (x_start + 5, y_start + height)], fill=self.line_color, width=3)
        
        x_end = x_start + width
        draw.line([(x_end, y_start), (x_end - 5, y_start)], fill=self.line_color, width=3)
        draw.line([(x_end, y_start), (x_end, y_start + height)], fill=self.line_color, width=3)
        draw.line([(x_end, y_start + height), (x_end - 5, y_start + height)], fill=self.line_color, width=3)
        
        # Numbers
        for r in range(rows):
            for c in range(cols):
                text = str(matrix[r, c])
                pos_x = x_start + c * cell_size + cell_size / 2
                pos_y = y_start + r * cell_size + cell_size / 2
                draw.text((pos_x, pos_y), text, fill=self.line_color, font=font, anchor="mm")
