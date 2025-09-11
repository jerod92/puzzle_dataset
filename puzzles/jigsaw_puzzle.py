# puzzles/jigsaw_puzzle.py

import random
from PIL import Image, ImageDraw
from .base_puzzle import BasePuzzle

class JigsawPuzzle(BasePuzzle):
    """
    Generates a jigsaw puzzle from an image sourced from a torchvision dataset.
    """
    def __init__(self, img_size, image_dataset=None):
        super().__init__(img_size)
        self.image_dataset = image_dataset

    def generate(self):
        # --- 1. Get a Source Image ---
        if self.image_dataset:
            # Pick a random image from the provided dataset
            random_index = random.randint(0, len(self.image_dataset) - 1)
            source_img, _ = self.image_dataset[random_index] # Dataset returns (image, label)
        else:
            # Fallback if no dataset was provided
            source_img = Image.new('RGB', (100, 100))
            draw = ImageDraw.Draw(source_img)
            draw.rectangle((0, 0, 100, 100), fill=random.choice(self.master_palette))
            draw.text((50, 50), "No Dataset!", anchor="mm", fill="white")

        # Resize image to fit the canvas and convert to RGB
        source_img = source_img.convert('RGB').resize((self.img_size, self.img_size))

        # The target image is the original, solved puzzle
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
        for i, tile in enumerate(tiles):
            x = (i % grid_size) * tile_size
            y = (i // grid_size) * tile_size
            input_image.paste(tile, (x, y))

        description = f"Rearrange the {grid_size}x{grid_size} tiles to solve the puzzle."
        return input_image, target_image, description
