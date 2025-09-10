# puzzles/move_to_target.py

import random
from PIL import ImageDraw
from .base_puzzle import BasePuzzle
from utils.drawing_utils import draw_shape

class MoveToTargetPuzzle(BasePuzzle):
    def generate(self):
        shapes = ['circle', 'triangle', 'square', 'diamond', 'star']
        shape_type = random.choice(shapes)
        color_hex = random.choice(self.master_palette)
        shape_size = self.img_size / 6

        padding = shape_size * 1.5
        
        start_pos = (
            random.uniform(padding, self.img_size - padding),
            random.uniform(padding, self.img_size - padding)
        )
        target_pos = (
            random.uniform(padding, self.img_size - padding),
            random.uniform(padding, self.img_size - padding)
        )
        
        # Ensure start and target are not too close
        while np.linalg.norm(np.array(start_pos) - np.array(target_pos)) < shape_size * 2:
            target_pos = (
                random.uniform(padding, self.img_size - padding),
                random.uniform(padding, self.img_size - padding)
            )

        # --- Create Input Image ---
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        
        # Draw the shape at the start
        draw_shape(draw_input, shape_type, start_pos, shape_size, color_hex)
        
        # Draw the 'X' target
        self._draw_x_target(draw_input, target_pos, shape_size / 2)
        
        # --- Create Target Image ---
        target_image = self._create_new_image()
        draw_target = ImageDraw.Draw(target_image)
        
        # Draw the shape at the target
        draw_shape(draw_target, shape_type, target_pos, shape_size, color_hex)

        description = f"Move the {shape_type} to the target 'X'."
        return input_image, target_image, description

    def _draw_x_target(self, draw, center, size):
        cx, cy = center
        draw.line((cx - size, cy - size, cx + size, cy + size), fill=self.line_color, width=5)
        draw.line((cx - size, cy + size, cx + size, cy - size), fill=self.line_color, width=5)
