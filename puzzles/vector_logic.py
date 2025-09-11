# puzzles/vector_logic.py

import random
import math
import numpy as np
from PIL import Image, ImageDraw
from .base_puzzle import BasePuzzle

class VectorLogicPuzzle(BasePuzzle):
    def generate(self):
        # --- 1. Setup Grid and Vectors ---
        grid_params = self._setup_grid()
        num_vectors = random.randint(2, 5)
        vectors = self._generate_vectors(num_vectors, grid_params)

        # --- 2. Choose and Generate a Specific Task ---
        possible_tasks = ['sum', 'chain']
        if len(vectors) == 2:
            possible_tasks.append('parallelogram')
        if len(vectors) > 1:
            possible_tasks.append('normalize')

        task_type = random.choice(possible_tasks)

        if task_type == 'chain':
            return self._generate_chain_task(vectors, grid_params)
        elif task_type == 'sum':
            return self._generate_sum_task(vectors, grid_params)
        elif task_type == 'parallelogram':
            return self._generate_parallelogram_task(vectors, grid_params)
        else: # normalize
            return self._generate_normalize_task(vectors, grid_params)

    # --- Task Generation Methods ---
    def _generate_chain_task(self, vectors, grid_params):
        random.shuffle(vectors)
        color_order_str = ", ".join([v['name'] for v in vectors])
        description = f"Join the vectors end to end in the order: {color_order_str}, starting at the origin."

        input_image = self._draw_vector_scene(vectors, [], grid_params)
        
        target_image = self._create_new_image()
        draw_target = ImageDraw.Draw(target_image)
        self._draw_grid(draw_target, grid_params)
        
        current_pos = np.array([0.0, 0.0])
        for vec in vectors:
            start_pixel = self._vec_to_pixel(current_pos, grid_params)
            end_pixel = self._vec_to_pixel(current_pos + vec['vec'], grid_params)
            self._draw_vector(draw_target, start_pixel, end_pixel, vec['color'])
            current_pos += vec['vec']

        return input_image, target_image, description

    def _generate_sum_task(self, vectors, grid_params):
        sum_color_hex, sum_color_name = random.choice(list(self.color_name_map.items()))
        description = f"Draw the vector that represents the sum of all vectors in {sum_color_name}, starting at the origin."

        input_image = self._draw_vector_scene(vectors, [], grid_params)
        
        target_image = self._create_new_image()
        draw_target = ImageDraw.Draw(target_image)
        self._draw_grid(draw_target, grid_params)

        sum_vec = np.sum([v['vec'] for v in vectors], axis=0)
        start_pixel = self._vec_to_pixel(np.array([0,0]), grid_params)
        end_pixel = self._vec_to_pixel(sum_vec, grid_params)
        self._draw_vector(draw_target, start_pixel, end_pixel, sum_color_hex)
        
        return input_image, target_image, description
        
    def _generate_parallelogram_task(self, vectors, grid_params):
        vec1, vec2 = vectors[0]['vec'], vectors[1]['vec']
        sum_vec = vec1 + vec2
        color = vectors[0]['color'] # Use the same color
        description = f"Draw the parallelogram created by the two vectors. Fill it with {vectors[0]['name']} at 50% transparency."

        input_image = self._draw_vector_scene(vectors, [], grid_params)

        target_image = input_image.copy()
        # Use RGBA to handle transparency
        target_image = target_image.convert("RGBA")
        draw_target = ImageDraw.Draw(target_image)
        
        # Define vertices in vector space
        p0 = self._vec_to_pixel(np.array([0,0]), grid_params)
        p1 = self._vec_to_pixel(vec1, grid_params)
        p2 = self._vec_to_pixel(vec2, grid_params)
        p_sum = self._vec_to_pixel(sum_vec, grid_params)
        
        # Create a transparent color
        r, g, b = Image.new("RGB", (1,1), color).getpixel((0,0))
        fill_color_rgba = (r, g, b, 128) # 50% transparency
        
        draw_target.polygon([p0, p1, p_sum, p2], fill=fill_color_rgba)
        
        return input_image, target_image.convert("RGB"), description

    def _generate_normalize_task(self, vectors, grid_params):
        mode = random.choice(['shortest', 'longest'])
        lengths = [np.linalg.norm(v['vec']) for v in vectors]
        target_length = min(lengths) if mode == 'shortest' else max(lengths)
        
        description = f"Normalize all vectors to the length of the {mode} vector."
        
        input_image = self._draw_vector_scene(vectors, [], grid_params)

        target_image = self._create_new_image()
        draw_target = ImageDraw.Draw(target_image)
        self._draw_grid(draw_target, grid_params)
        
        origin_pixel = self._vec_to_pixel(np.array([0,0]), grid_params)
        for vec in vectors:
            norm_vec = (vec['vec'] / np.linalg.norm(vec['vec'])) * target_length
            end_pixel = self._vec_to_pixel(norm_vec, grid_params)
            self._draw_vector(draw_target, origin_pixel, end_pixel, vec['color'])
            
        return input_image, target_image, description

    # --- Drawing and Helper Methods ---
    def _setup_grid(self):
        padding = self.img_size * 0.1
        axis_range = (-5, 5)
        num_ticks = axis_range[1] - axis_range[0]
        scale = (self.img_size - 2 * padding) / num_ticks
        origin = (self.img_size / 2, self.img_size / 2)
        return {'padding': padding, 'axis_range': axis_range, 'scale': scale, 'origin': origin}

    def _generate_vectors(self, num_vectors, grid_params):
        vectors = []
        colors = random.sample(self.master_palette, num_vectors)
        for i in range(num_vectors):
            vec = np.random.uniform(-4.5, 4.5, 2)
            vectors.append({
                'vec': vec,
                'color': colors[i],
                'name': self.color_name_map[colors[i]]
            })
        return vectors

    def _vec_to_pixel(self, vec, grid_params):
        ox, oy = grid_params['origin']
        scale = grid_params['scale']
        return (ox + vec[0] * scale, oy - vec[1] * scale)

    def _draw_vector_scene(self, vectors, points, grid_params):
        img = self._create_new_image()
        draw = ImageDraw.Draw(img)
        self._draw_grid(draw, grid_params)
        origin_pixel = self._vec_to_pixel(np.array([0,0]), grid_params)
        for vec in vectors:
            end_pixel = self._vec_to_pixel(vec['vec'], grid_params)
            self._draw_vector(draw, origin_pixel, end_pixel, vec['color'])
        return img

    def _draw_vector(self, draw, p1, p2, color):
        x1, y1 = p1
        x2, y2 = p2
        draw.line([p1, p2], fill=color, width=4)
        # Arrowhead
        angle = math.atan2(y2 - y1, x2 - x1)
        arrow_len = 15
        a1 = angle + math.pi * 0.8
        a2 = angle - math.pi * 0.8
        p_a1 = (x2 + arrow_len * math.cos(a1), y2 + arrow_len * math.sin(a1))
        p_a2 = (x2 + arrow_len * math.cos(a2), y2 + arrow_len * math.sin(a2))
        draw.polygon([p2, p_a1, p_a2], fill=color)

    def _draw_grid(self, draw, grid_params):
        padding = grid_params['padding']
        s = self.img_size
        num_ticks = grid_params['axis_range'][1] - grid_params['axis_range'][0]
        step = (s - 2 * padding) / num_ticks
        for i in range(num_ticks + 1):
            pos = padding + i * step
            draw.line([(pos, padding), (pos, s - padding)], fill='#e0e0e0', width=1)
            draw.line([(padding, pos), (s - padding, pos)], fill='#e0e0e0', width=1)
        draw.line([(s/2, padding), (s/2, s-padding)], fill=self.line_color, width=2)
        draw.line([(padding, s/2), (s-padding, s/2)], fill=self.line_color, width=2)
