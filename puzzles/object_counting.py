# puzzles/object_counting.py

import random
import numpy as np
from PIL import ImageDraw, ImageFont
from .base_puzzle import BasePuzzle
from utils.drawing_utils import draw_shape

class ObjectCountingPuzzle(BasePuzzle):
    """
    Generates a puzzle where the user must count or identify objects.
    
    The task can be one of three types:
    1. Count a specific type of object.
    2. Identify the most common type of object.
    3. Count the number of distinct object types.
    """
    def generate(self):
        # --- 1. Setup Puzzle Parameters ---
        num_types = random.choice([1, 2, 3])
        total_objects = random.randint(8, 20)
        
        all_shapes = ['circle', 'square', 'triangle', 'diamond', 'star', 'hexagon']
        chosen_shapes = random.sample(all_shapes, num_types)
        chosen_colors = random.sample(self.master_palette, num_types)
        
        object_prototypes = [{'shape': s, 'color': c, 'name': f"{self.color_name_map[c]} {s}s"} for s, c in zip(chosen_shapes, chosen_colors)]

        # --- 2. Generate the list of objects and their counts ---
        objects_to_draw = []
        counts = {proto['name']: 0 for proto in object_prototypes}
        for proto in object_prototypes:
            objects_to_draw.append(proto)
            counts[proto['name']] += 1
        for _ in range(total_objects - num_types):
            chosen_proto = random.choice(object_prototypes)
            objects_to_draw.append(chosen_proto)
            counts[chosen_proto['name']] += 1

        # --- 3. Determine the Prompt and Target Answer ---
        possible_prompts = ['specific_count']
        if num_types > 1:
            possible_prompts.append('distinct_count')
            max_count = max(counts.values())
            if list(counts.values()).count(max_count) == 1:
                possible_prompts.append('most_common_object')
        
        chosen_prompt = random.choice(possible_prompts)
        
        target_answer_data = None
        description = ""

        if chosen_prompt == 'most_common_object':
            target_name = max(counts, key=counts.get)
            # Find the full object prototype to use as the answer
            target_answer_data = next(p for p in object_prototypes if p['name'] == target_name)
            description = "Fill in the box with the most common object."
        
        elif chosen_prompt == 'distinct_count':
            target_answer_data = num_types
            description = "Fill in the box with the number of distinct object types."

        else: # specific_count
            target_prototype = random.choice(object_prototypes)
            target_name = target_prototype['name']
            target_answer_data = counts[target_name]
            description = f"Fill in the box with the correct number of {target_name}."

        # --- 4. Draw the Images ---
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        
        box_width = self.img_size * 0.18
        padding = self.img_size * 0.05
        draw_area_x_min = box_width + padding
        
        self._draw_scattered_objects(draw_input, objects_to_draw, draw_area_x_min, padding)
        box_coords = self._draw_query_box(draw_input, box_width, padding, "?")
        
        target_image = input_image.copy()
        draw_target = ImageDraw.Draw(target_image)
        
        # Fill in the box with the correct answer (object or number)
        draw_target.rectangle(box_coords, fill=self.bg_color, outline=self.line_color, width=4)
        if chosen_prompt == 'most_common_object':
            self._draw_shape_in_box(draw_target, box_coords, target_answer_data)
        else:
            self._draw_text_in_box(draw_target, box_coords, str(target_answer_data))

        return input_image, target_image, description

    def _draw_scattered_objects(self, draw, objects, x_min, padding):
        object_size = self.img_size / 15
        placed_positions = []

        for obj in objects:
            pos = (0, 0)
            for _ in range(10): # Max attempts to find a non-overlapping spot
                pos = (random.uniform(x_min, self.img_size - padding), random.uniform(padding, self.img_size - padding))
                if not any(np.linalg.norm(np.array(pos) - np.array(p)) < object_size * 1.5 for p in placed_positions):
                    break
            placed_positions.append(pos)
            draw_shape(draw, obj['shape'], pos, object_size, obj['color'])

    def _draw_query_box(self, draw, box_width, padding, text):
        box_height = box_width * 1.2
        box_x0 = padding / 2
        box_y0 = (self.img_size - box_height) / 2
        box_coords = (box_x0, box_y0, box_x0 + box_width, box_y0 + box_height)
        
        draw.rectangle(box_coords, outline=self.line_color, width=4)
        self._draw_text_in_box(draw, box_coords, text)
        return box_coords

    def _draw_text_in_box(self, draw, box_coords, text):
        center_x = (box_coords[0] + box_coords[2]) / 2
        center_y = (box_coords[1] + box_coords[3]) / 2
        font_size = int((box_coords[3] - box_coords[1]) * 0.6)
        try: font = ImageFont.load_default(size=font_size)
        except AttributeError: font = ImageFont.load_default()
        draw.text((center_x, center_y), text, fill=self.line_color, font=font, anchor="mm")

    def _draw_shape_in_box(self, draw, box_coords, prototype):
        center_x = (box_coords[0] + box_coords[2]) / 2
        center_y = (box_coords[1] + box_coords[3]) / 2
        # Make the shape slightly smaller than the box
        shape_size = (box_coords[2] - box_coords[0]) * 0.6
        draw_shape(draw, prototype['shape'], (center_x, center_y), shape_size, prototype['color'])
