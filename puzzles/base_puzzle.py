# puzzles/base_puzzle.py
from abc import ABC, abstractmethod
from PIL import Image, ImageDraw, ImageFont
from utils.color_palette import MASTER_PALETTE, COLOR_NAME_MAP

class BasePuzzle(ABC):
    """Abstract base class for all puzzle generators."""
    def __init__(self, img_size):
        self.img_size = img_size
        self.bg_color = 'white'
        self.line_color = 'black'
        self.master_palette = MASTER_PALETTE
        self.color_name_map = COLOR_NAME_MAP

    @abstractmethod
    def generate(self, *args, **kwargs):
        """
        The main method to generate a puzzle.
        Should return a tuple of (input_image, target_image, text_description).
        """
        pass

    def _create_new_image(self):
        """Creates a new blank RGB image."""
        return Image.new('RGB', (self.img_size, self.img_size), self.bg_color)