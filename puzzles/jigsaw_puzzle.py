# puzzles/jigsaw_puzzle.py

import random
import os
from PIL import Image, ImageDraw
from .base_puzzle import BasePuzzle

class JigsawPuzzle(BasePuzzle):
    def generate(self):
        image_folder = 'jigsaw_images'
        
        try:
            available_images = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not available_images:
                raise FileNotFoundError
            
            image_path = os.path.join(image_folder, random.choice(available_images))
            source_img = Image.open(image_path).convert('RGB')
        except (FileNotFoundError, IndexError):
            # Fallback if no images are found
            source_img = Image.new('RGB', (100, 100))
            draw = ImageDraw.Draw(source_img)
            draw.rectangle((0, 0, 100, 100), fill=random.choice(self.master_palette))
            draw.text((50, 50), "No Image Found!", anchor="mm", fill="white")

        # Resize image to fit the canvas and make it square
        source_img = source_img.resize((self.img_size, self.img_size))

        # The target image is simply the solved puzzle
        target_image = source_img

        # --- Create Input Image ---
        grid_size = random.choice([2, 3, 4])
        tile_size = self.img_size // grid_size
        
        # Create a list of tiles
        tiles = []
        for y in range(grid_size):
            for x in range(grid_size):
                box = (x * tile_size, y * tile_size, (x + 1) * tile_size, (y + 1) * tile_size)
                tiles.append(source_img.crop(box))
        
        # Shuffle the tiles
        random.shuffle(tiles)
        
        # Create the input image by pasting the shuffled tiles
        input_image = self._create_new_image()
        for i, tile in enumerate(tiles):
            x = (i % grid_size) * tile_size
            y = (i // grid_size) * tile_size
            input_image.paste(tile, (x, y))

        description = f"Rearrange the {grid_size}x{grid_size} tiles to solve the puzzle."
        return input_image, target_image, description
