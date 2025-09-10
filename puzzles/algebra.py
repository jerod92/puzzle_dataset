# puzzles/algebra.py
import random
from PIL import ImageDraw, ImageFont
from .base_puzzle import BasePuzzle

class AlgebraPuzzle(BasePuzzle):
    def generate(self):
        variable = random.choice(['x', 'y', 'z'])
        solution = random.randint(-5, 6)
        
        a = random.randint(1, 6)
        b = random.randint(-10, 11)
        c = a * solution + b
        
        problem_str = f"{a}{variable} {'+' if b >= 0 else '-'} {abs(b)} = {c}\n\n{variable} = ?"
        answer_str = f"{a}{variable} {'+' if b >= 0 else '-'} {abs(b)} = {c}\n\n{variable} = {solution}"
        
        try:
            font = ImageFont.load_default(size=40)
        except AttributeError:
            font = ImageFont.load_default()
        
        # Create input image
        input_image = self._create_new_image()
        draw_in = ImageDraw.Draw(input_image)
        draw_in.text((self.img_size/2, self.img_size/2), problem_str, fill=self.line_color, font=font, anchor='mm', align='center')
        
        # Create target image
        target_image = self._create_new_image()
        draw_out = ImageDraw.Draw(target_image)
        draw_out.text((self.img_size/2, self.img_size/2), answer_str, fill=self.line_color, font=font, anchor='mm', align='center')
        
        description = "Please solve for the variable."
        
        return input_image, target_image, description