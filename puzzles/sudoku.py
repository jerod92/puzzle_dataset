# puzzles/sudoku.py
import random
from PIL import ImageDraw, ImageFont
from .base_puzzle import BasePuzzle

class SudokuPuzzle(BasePuzzle):
    def generate(self, puzzle_data):
        """
        Generates a Sudoku puzzle.
        
        Args:
            puzzle_data (tuple): A tuple containing the quiz string and the solution string.
        """
        puzzle_str, solution_str = puzzle_data
        
        # Randomly reveal some of the missing numbers to vary difficulty
        puzzle_list = list(puzzle_str)
        missing_indices = [i for i, char in enumerate(puzzle_str) if char == '0']
        
        if missing_indices: # Avoid error if the puzzle is already solved
            indices_to_reveal = random.sample(missing_indices, random.randint(0, len(missing_indices)))
            for i in indices_to_reveal:
                puzzle_list[i] = solution_str[i]
        
        input_image = self._generate_sudoku_image("".join(puzzle_list))
        target_image = self._generate_sudoku_image(solution_str)
        description = "Solve this sudoku puzzle."
        
        return input_image, target_image, description

    def _generate_sudoku_image(self, puzzle_string):
        img = self._create_new_image()
        draw = ImageDraw.Draw(img)
        cell_size = self.img_size / 9
        
        try:
            # A larger default font
            font = ImageFont.load_default(size=30)
        except AttributeError:
            # Fallback for older Pillow versions
            font = ImageFont.load_default()

        # Draw grid lines
        for i in range(10):
            width = 3 if i % 3 == 0 else 1
            draw.line([(i * cell_size, 0), (i * cell_size, self.img_size)], fill=self.line_color, width=width)
            draw.line([(0, i * cell_size), (self.img_size, i * cell_size)], fill=self.line_color, width=width)

        # Draw numbers
        for i in range(81):
            if puzzle_string[i] != '0':
                row, col = i // 9, i % 9
                text_position = (col * cell_size + cell_size * 0.5, row * cell_size + cell_size * 0.5)
                draw.text(text_position, puzzle_string[i], fill=self.line_color, font=font, anchor='mm')
                
        return img