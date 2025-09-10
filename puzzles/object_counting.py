# puzzles/object_counting.py

import random
import numpy as np
from PIL import ImageDraw, ImageFont
from .base_puzzle import BasePuzzle
from utils.drawing_utils import draw_shape

class ObjectCountingPuzzle(BasePuzzle):
    """
    Generates a puzzle where the user must count scattered objects.
    
    The task can be one of two types:
    1. Count a specific type of object.
    2. Count the most common type of object.
    """
    def generate(self):
        # --- 1. Setup Puzzle Parameters ---
        num_types = random.choice([1, 2, 3])
        total_objects = random.randint(8, 20)
        
        # Select unique shapes and colors for the objects
        all_shapes = ['circle', 'square', 'triangle', 'diamond', 'star', 'hexagon']
        chosen_shapes = random.sample(all_shapes, num_types)
        chosen_colors = random.sample(self.master_palette, num_types)
        
        # Create a list of object prototypes to choose from
        object_prototypes = []
        for i in range(num_types):
            object_prototypes.append({
                'shape': chosen_shapes[i],
                'color': chosen_colors[i],
                'name': f"{self.color_name_map[chosen_colors[i]]} {chosen_shapes[i]}s"
            })

        # --- 2. Generate the list of objects and their counts ---
        objects_to_draw = []
        counts = {proto['name']: 0 for proto in object_prototypes}

        # Ensure each type appears at least once
        for proto in object_prototypes:
            objects_to_draw.append(proto)
            counts[proto['name']] += 1
        
        # Add the rest of the objects randomly
        for _ in range(total_objects - num_types):
            chosen_proto = random.choice(object_prototypes)
            objects_to_draw.append(chosen_proto)
            counts[chosen_proto['name']] += 1

        # --- 3. Determine the Prompt and Target Answer ---
        use_most_common_prompt = False
        if num_types > 1:
            max_count = max(counts.values())
            # Check if the max count is unique to avoid ambiguity
            if list(counts.values()).count(max_count) == 1:
                use_most_common_prompt = random.choice([True, False])

        if use_most_common_prompt:
            # Find the most common object
            target_name = max(counts, key=counts.get)
            target_answer = counts[target_name]
            description = "Fill in the box with the count of the most common object."
        else:
            # Pick a random object type to count
            target_prototype = random.choice(object_prototypes)
            target_name = target_prototype['name']
            target_answer = counts[target_name]
            description = f"Fill in the box with the correct number of {target_name}."

        # --- 4. Draw the Images ---
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        
        # Define areas for the box and the objects
        box_width = self.img_size * 0.18
        padding = self.img_size * 0.05
        draw_area_x_min = box_width + padding
        
        # Scatter the objects
        self._draw_scattered_objects(draw_input, objects_to_draw, draw_area_x_min, padding)
        
        # Draw the empty query box
        box_coords = self._draw_query_box(draw_input, box_width, padding, "?")
        
        # Create target image
        target_image = input_image.copy()
        draw_target = ImageDraw.Draw(target_image)
        
        # Fill in the box with the correct number
        draw_target.rectangle(box_coords, fill=self.bg_color, outline=self.line_color, width=4)
        self._draw_text_in_box(draw_target, box_coords, str(target_answer))

        return input_image, target_image, description

    def _draw_scattered_objects(self, draw, objects, x_min, padding):
        object_size = self.img_size / 15
        placed_positions = []

        for obj in objects:
            for _ in range(10): # Max 10 attempts to find a non-overlapping spot
                pos = (
                    random.uniform(x_min, self.img_size - padding),
                    random.uniform(padding, self.img_size - padding)
                )
                
                # Simple collision detection
                is_overlapping = False
                for placed_pos in placed_positions:
                    if np.linalg.norm(np.array(pos) - np.array(placed_pos)) < object_size * 1.5:
                        is_overlapping = True
                        break
                
                if not is_overlapping:
                    break
            
            placed_positions.append(pos)
            draw_shape(draw, obj['shape'], pos, object_size, obj['color'])

    def _draw_query_box(self, draw, box_width, padding, text):
        box_height = box_width * 1.2
        box_x0 = padding / 2
        box_y0 = (self.img_size - box_height) / 2
        box_x1 = box_x0 + box_width
        box_y1 = box_y0 + box_height
        box_coords = (box_x0, box_y0, box_x1, box_y1)
        
        draw.rectangle(box_coords, outline=self.line_color, width=4)
        self._draw_text_in_box(draw, box_coords, text)
        return box_coords

    def _draw_text_in_box(self, draw, box_coords, text):
        box_x0, box_y0, box_x1, box_y1 = box_coords
        center_x = (box_x0 + box_x1) / 2
        center_y = (box_y0 + box_y1) / 2
        
        font_size = int((box_y1 - box_y0) * 0.6)
        try:
            font = ImageFont.load_default(size=font_size)
        except AttributeError:
            font = ImageFont.load_default()
            
        draw.text((center_x, center_y), text, fill=self.line_color, font=font, anchor="mm")
