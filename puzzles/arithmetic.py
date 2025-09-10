# puzzles/arithmetic.py
import random
from PIL import ImageDraw, ImageFont
from .base_puzzle import BasePuzzle

class ArithmeticPuzzle(BasePuzzle):
    def generate(self):
        try:
            font = ImageFont.load_default(size=50)
        except AttributeError:
            font = ImageFont.load_default()
            
        if random.random() > 0.4:
            # Simple arithmetic
            a, b = random.randint(1, 10), random.randint(1, 10)
            op = random.choice(['+', 'x'])
            problem_str = f"{a} {op} {b} = ?"
            answer = a + b if op == '+' else a * b
        else:
            # With parentheses
            a, b, c = random.randint(1, 9), random.randint(1, 9), random.randint(2, 5)
            if random.random() > 0.5:
                problem_str = f"({a} + {b}) x {c} = ?"
                answer = (a + b) * c
            else:
                problem_str = f"{a} + ({b} x {c}) = ?"
                answer = a + (b * c)
        
        answer_str = problem_str.replace('?', str(answer))
        
        # Create images
        input_image = self._create_new_image()
        draw_in = ImageDraw.Draw(input_image)
        draw_in.text((self.img_size/2, self.img_size/2), problem_str, fill=self.line_color, font=font, anchor='mm')
        
        target_image = self._create_new_image()
        draw_out = ImageDraw.Draw(target_image)
        draw_out.text((self.img_size/2, self.img_size/2), answer_str, fill=self.line_color, font=font, anchor='mm')
        
        description = "Please replace the question mark with the correct number."
        
        return input_image, target_image, description