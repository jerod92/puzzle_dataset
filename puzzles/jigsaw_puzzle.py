# puzzles/jigsaw_puzzle.py

import random
from PIL import Image, ImageDraw
from .base_puzzle import BasePuzzle

class JigsawPuzzle(BasePuzzle):
    """
    Generates a jigsaw puzzle from an image sourced from a torchvision dataset.
    The shuffled tiles are displayed with gaps between them for clarity.
    """
    def __init__(self, img_size, image_dataset=None):
        super().__init__(img_size)
        self.image_dataset = image_dataset

    def generate(self):
        # --- 1. Get a Source Image ---
        if self.image_dataset:
            random_index = random.randint(0, len(self.image_dataset) - 1)
            source_img, _ = self.image_dataset[random_index]
        else: # Fallback
            source_img = Image.new('RGB', (100, 100), random.choice(self.master_palette))

        source_img = source_img.convert('RGB').resize((self.img_size, self.img_size))
        target_image = source_img

        # --- 2. Create the Shuffled Input Image ---
        grid_size = random.choice([2, 3, 4])
        tile_size = self.img_size // grid_size
        
        tiles = []
        for y in range(grid_size):
            for x in range(grid_size):
                box = (x * tile_size, y * tile_size, (x + 1) * tile_size, (y + 1) * tile_size)
                tiles.append(source_img.crop(box))
        
        random.shuffle(tiles)
        
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        
        # --- NEW: Draw the grid to create gaps ---
        gap_width = 4
        for i in range(grid_size + 1):
            pos_y = i * tile_size
            pos_x = i * tile_size
            # Clamp position to avoid drawing outside the image border
            pos_y = min(pos_y, self.img_size - 1)
            pos_x = min(pos_x, self.img_size - 1)
            draw_input.line([(0, pos_y), (self.img_size, pos_y)], fill=self.line_color, width=gap_width)
            draw_input.line([(pos_x, 0), (pos_x, self.img_size)], fill=self.line_color, width=gap_width)
        
        # Paste the shuffled tiles onto the grid
        for i, tile in enumerate(tiles):
            x = (i % grid_size) * tile_size
            y = (i // grid_size) * tile_size
            input_image.paste(tile, (x, y))

        description = f"Rearrange the {grid_size}x{grid_size} tiles to solve the puzzle."
        return input_image, target_image, description
