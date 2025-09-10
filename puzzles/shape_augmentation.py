# puzzles/shape_augmentation.py
import random
from PIL import ImageDraw
from .base_puzzle import BasePuzzle
from utils.drawing_utils import draw_shape

class ShapeAugmentationPuzzle(BasePuzzle):
    def generate(self):
        shapes = ['circle', 'triangle', 'hexagon', 'square', 'diamond', 'trapezoid', 'arrow', 'star']
        
        # Initial parameters
        shape = random.choice(shapes)
        color_hex = random.choice(self.master_palette)
        bg_color_hex = '#FFFFFF'
        center = (self.img_size / 2, self.img_size / 2)
        size = self.img_size / 3
        
        # Draw input image
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        draw_shape(draw_input, shape, center, size, color_hex)
        
        # Choose and apply a transformation
        target_params, description = self._get_random_transformation(shape, color_hex, bg_color_hex, center, size)
        
        # Draw target image
        target_image = self._create_new_image()
        target_image.paste(target_params['bg_color'])
        draw_target = ImageDraw.Draw(target_image)
        draw_shape(
            draw_target,
            target_params['shape'],
            target_params['center'],
            target_params['size'],
            target_params['color'],
            rotation=target_params['rotation'],
            scale=target_params['scale'],
            border_color=target_params['border_color']
        )
        
        return input_image, target_image, description

    def _get_random_transformation(self, shape, color, bg_color, center, size):
        params = {
            'shape': shape, 'color': color, 'bg_color': bg_color,
            'center': center, 'size': size, 'rotation': 0,
            'scale': (1, 1), 'border_color': None
        }
        
        transformation = random.randint(1, 10)
        desc = ""
        
        if transformation == 1: # rotate
            degrees = random.randint(30, 180)
            direction = random.choice(['clockwise', 'counterclockwise'])
            params['rotation'] = degrees if direction == 'clockwise' else -degrees
            desc = f"rotate the {shape} {degrees} degrees {direction}"
        elif transformation == 2: # flip
            direction = random.choice(['horizontally', 'vertically'])
            params['scale'] = (-1, 1) if direction == 'horizontally' else (1, -1)
            desc = f"flip the {shape} {direction}"
        elif transformation == 3: # change color
            new_color_hex, new_color_name = random.choice(list(self.color_name_map.items()))
            params['color'] = new_color_hex
            desc = f"change to {new_color_name}"
        elif transformation == 4: # shrink/blow up
            factor = random.choice([0.5, 2])
            params['size'] = size * factor
            desc = "shrink" if factor == 0.5 else "blow up"
        elif transformation == 5: # stretch
            direction = random.choice(['horizontally', 'vertically'])
            factor = random.choice([0.5, 2])
            params['scale'] = (factor, 1) if direction == 'horizontally' else (1, factor)
            desc = f"stretch {direction}"
        elif transformation == 6: # change background
            new_bg_hex, new_bg_name = random.choice(list(self.color_name_map.items()))
            params['bg_color'] = new_bg_hex
            desc = f"change background color to {new_bg_name}"
        elif transformation == 7: # move to corner
            corner_y = random.choice(['top', 'bottom'])
            corner_x = random.choice(['left', 'right'])
            padding = size / 1.5
            params['center'] = (
                padding if corner_x == 'left' else self.img_size - padding,
                padding if corner_y == 'top' else self.img_size - padding
            )
            desc = f"Move to the {corner_y}-{corner_x} corner"
        elif transformation == 8: # move to edge
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            padding = size / 1.5
            if edge == 'top': params['center'] = (self.img_size/2, padding)
            elif edge == 'bottom': params['center'] = (self.img_size/2, self.img_size-padding)
            elif edge == 'left': params['center'] = (padding, self.img_size/2)
            else: params['center'] = (self.img_size-padding, self.img_size/2)
            desc = f"Move to the {edge} of the screen"
        elif transformation == 9: # replace
            shapes = ['circle', 'triangle', 'hexagon', 'square', 'diamond', 'trapezoid', 'arrow', 'star']
            params['shape'] = random.choice([s for s in shapes if s != shape])
            desc = f"Replace with {params['shape']}"
        else: # Add border
            border_color_hex, border_color_name = random.choice(list(self.color_name_map.items()))
            params['border_color'] = border_color_hex
            desc = f"Add a {border_color_name} border to {shape}"
            
        return params, desc