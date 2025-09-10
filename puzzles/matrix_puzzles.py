# puzzles/matrix_puzzles.py
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from .base_puzzle import BasePuzzle
from utils.drawing_utils import rotate_points

# --- Base Class for all 3x3 Matrix Puzzles ---
class BaseMatrixPuzzle(BasePuzzle):
    """A base class for 3x3 grid puzzles to handle common drawing logic."""
    def __init__(self, img_size):
        super().__init__(img_size)
        self.grid_size = 3
        self.panel_size = self.img_size // self.grid_size

    def generate(self):
        panels, description = self._generate_panels()
        input_image, target_image = self._build_images_from_panels(panels)
        return input_image, target_image, description

    def _generate_panels(self):
        """This method should be implemented by subclasses."""
        raise NotImplementedError

    def _build_images_from_panels(self, panels):
        # Create the complete target image
        target_image = self._create_new_image()
        for i in range(len(panels)):
            row, col = i // self.grid_size, i % self.grid_size
            target_image.paste(panels[i], (col * self.panel_size, row * self.panel_size))
        
        draw_target = ImageDraw.Draw(target_image)
        self._draw_gridlines(draw_target)

        # Create the input image by blanking out the last panel
        input_image = target_image.copy()
        draw_input = ImageDraw.Draw(input_image)
        
        final_cell_origin = ((self.grid_size - 1) * self.panel_size, (self.grid_size - 1) * self.panel_size)
        draw_input.rectangle([final_cell_origin, (self.img_size, self.img_size)], fill=self.bg_color)
        
        self._draw_gridlines(draw_input)
        
        # Draw question mark
        try:
            q_font = ImageFont.load_default(size=self.panel_size // 4)
        except AttributeError:
            q_font = ImageFont.load_default()
        q_pos = (final_cell_origin[0] + self.panel_size/2, final_cell_origin[1] + self.panel_size/2)
        draw_input.text(q_pos, "?", fill=self.line_color, font=q_font, anchor='mm')
        
        return input_image, target_image

    def _draw_gridlines(self, draw):
        for i in range(1, self.grid_size):
            draw.line([(i * self.panel_size, 0), (i * self.panel_size, self.img_size)], fill=self.line_color, width=2)
            draw.line([(0, i * self.panel_size), (self.img_size, i * self.panel_size)], fill=self.line_color, width=2)

    def _draw_matrix_panel(self, quadrant_colors, shape, shape_rotation=0):
        img = Image.new('RGB', (self.panel_size, self.panel_size), self.bg_color)
        draw = ImageDraw.Draw(img)
        center = (self.panel_size / 2, self.panel_size / 2)
        size = self.panel_size / 3.5

        if shape == 'dots':
            ps = self.panel_size
            dot_size = ps * 0.15
            positions = [
                (ps*.25-dot_size, ps*.25-dot_size, ps*.25+dot_size, ps*.25+dot_size),
                (ps*.75-dot_size, ps*.25-dot_size, ps*.75+dot_size, ps*.25+dot_size),
                (ps*.25-dot_size, ps*.75-dot_size, ps*.25+dot_size, ps*.75+dot_size),
                (ps*.75-dot_size, ps*.75-dot_size, ps*.75+dot_size, ps*.75+dot_size)
            ]
            for color, pos in zip(quadrant_colors, positions):
                if color: draw.ellipse(pos, fill=color)
        else:
            polys = []
            if shape == 'square':
                polys = [
                    [center, (center[0]+size,center[1]),(center[0]+size,center[1]-size),(center[0],center[1]-size)],
                    [center, (center[0]-size,center[1]),(center[0]-size,center[1]+size),(center[0],center[1]+size)],
                    [center, (center[0]-size,center[1]),(center[0]-size,center[1]-size),(center[0],center[1]-size)],
                    [center, (center[0]+size,center[1]),(center[0]+size,center[1]+size),(center[0],center[1]+size)]
                ]
            elif shape == 'diamond':
                p = [(center[0],center[1]-size),(center[0]+size,center[1]),(center[0],center[1]+size),(center[0]-size,center[1])]
                polys = [[center,p[0],p[1]],[center,p[1],p[2]],[center,p[2],p[3]],[center,p[3],p[0]]]
            elif shape == 'triangle':
                p = [(center[0],center[1]-size),(center[0]+size,center[1]+size*.8),(center[0]-size,center[1]+size*.8)]
                m1,m2,m3 = ((p[0][0]+p[1][0])/2,(p[0][1]+p[1][1])/2),((p[1][0]+p[2][0])/2,(p[1][1]+p[2][1])/2),((p[2][0]+p[0][0])/2,(p[2][1]+p[0][1])/2)
                polys = [[center,p[0],m1],[center,m1,p[1],m2],[center,m2,p[2],m3],[center,m3,p[0]]]
            
            rotated = [rotate_points(poly, center, shape_rotation) for poly in polys]
            for color, poly in zip(quadrant_colors, rotated):
                if color: draw.polygon(poly, fill=color)
        return img

# --- Individual Matrix Puzzle Generators ---

class RotationMatrixPuzzle(BaseMatrixPuzzle):
    def _generate_panels(self):
        shape = random.choice(['square', 'diamond', 'triangle', 'dots'])
        angle = 45 if shape == 'diamond' else 90
        panels = []
        colors = random.sample(self.master_palette, 2)
        quad_colors = [colors[0], colors[1], None, None]
        random.shuffle(quad_colors)
        
        for i in range(self.grid_size * self.grid_size):
            r, c = i // self.grid_size, i % self.grid_size
            current_angle = (r + c) * angle 
            panels.append(self._draw_matrix_panel(quad_colors, shape=shape, shape_rotation=current_angle))
            
        return panels, "Please fill in the missing cell based on the rotation pattern."

class FillProgressionMatrixPuzzle(BaseMatrixPuzzle):
    def _generate_panels(self):
        panels = []
        shape = random.choice(['square', 'diamond', 'triangle', 'dots'])
        for r in range(self.grid_size):
            color = random.choice(self.master_palette)
            start_n = random.randint(1, 2)
            quad_indices = list(range(4))
            random.shuffle(quad_indices)  # Shuffle once per row
            
            for c in range(self.grid_size):
                num_to_fill = min(4, start_n + c)
                quads_to_fill = quad_indices[:num_to_fill]
                quad_colors = [color if i in quads_to_fill else None for i in range(4)]
                panels.append(self._draw_matrix_panel(quad_colors, shape))
                
        return panels, "Please fill in the missing cell based on the fill progression."

class MonochromeLogicMatrixPuzzle(BaseMatrixPuzzle):
    def _generate_panels(self):
        op = random.choice(['XOR', 'UNION', 'INTERSECTION'])
        panels = []
        shape = random.choice(['square', 'diamond', 'triangle', 'dots'])
        for _ in range(self.grid_size):
            color = random.choice(self.master_palette)
            q_a = [color if random.random() > 0.5 else None for _ in range(4)]
            q_b = [color if random.random() > 0.5 else None for _ in range(4)]
            q_c = []
            
            for qa, qb in zip(q_a, q_b):
                res = None
                if op == 'XOR' and ((qa is not None) ^ (qb is not None)): res = color
                if op == 'UNION' and ((qa is not None) or (qb is not None)): res = color
                if op == 'INTERSECTION' and ((qa is not None) and (qb is not None)): res = color
                q_c.append(res)
                
            panels.extend([
                self._draw_matrix_panel(q_a, shape),
                self._draw_matrix_panel(q_b, shape),
                self._draw_matrix_panel(q_c, shape)
            ])
            
        return panels, f"Please fill in the missing cell based on the {op} logic."

class TricolorRotationMatrixPuzzle(BaseMatrixPuzzle):
    def _generate_panels(self):
        panels = []
        shape = random.choice(['square', 'diamond', 'triangle', 'dots'])
        colors = random.sample(self.master_palette, 3)
        color_map = {colors[0]: colors[1], colors[1]: colors[2], colors[2]: colors[0]}
        
        for _ in range(self.grid_size):
            quads_a = list(np.random.choice(colors + [None], 4))
            quads_b = [color_map.get(q) for q in quads_a]
            quads_c = [color_map.get(q) for q in quads_b]
            panels.extend([
                self._draw_matrix_panel(quads_a, shape),
                self._draw_matrix_panel(quads_b, shape),
                self._draw_matrix_panel(quads_c, shape)
            ])
            
        return panels, "Please fill in the missing cell based on the color rotation."

class LatinSquareMatrixPuzzle(BaseMatrixPuzzle):
    def _generate_panels(self):
        shapes = random.sample(['square', 'diamond', 'triangle', 'dots'], 3)
        color = random.choice(self.master_palette)
        quad_colors = [color if random.random() > 0.3 else None for _ in range(4)]
        
        row0 = np.random.permutation(shapes)
        grid_shapes = np.array([np.roll(row0, i) for i in range(self.grid_size)])
        if random.random() > 0.5:
            grid_shapes = grid_shapes.T
            
        panels = [self._draw_matrix_panel(quad_colors, shape=s) for s in grid_shapes.flatten()]
        return panels, "Please fill in the missing cell to complete the Latin Square."

class ShapeSuperpositionMatrixPuzzle(BaseMatrixPuzzle):
    def _generate_panels(self):
        panels = []
        ps = self.panel_size
        pos = [
            (ps*.1, ps*.1, ps*.4, ps*.4), (ps*.6, ps*.1, ps*.9, ps*.4),
            (ps*.1, ps*.6, ps*.4, ps*.9), (ps*.6, ps*.6, ps*.9, ps*.9)
        ]
        
        for _ in range(self.grid_size):
            color = random.choice(self.master_palette)
            ind_a = set(np.random.choice(4, random.randint(1, 3), replace=False))
            ind_b = set(np.random.choice(4, random.randint(1, 3), replace=False))
            ind_c = ind_a.union(ind_b)
            
            img_a = Image.new('RGB', (ps, ps), self.bg_color)
            draw_a = ImageDraw.Draw(img_a)
            img_b = Image.new('RGB', (ps, ps), self.bg_color)
            draw_b = ImageDraw.Draw(img_b)
            img_c = Image.new('RGB', (ps, ps), self.bg_color)
            draw_c = ImageDraw.Draw(img_c)

            for i in ind_a: draw_a.ellipse(pos[i], fill=color)
            for i in ind_b: draw_b.ellipse(pos[i], fill=color)
            for i in ind_c: draw_c.ellipse(pos[i], fill=color)
            
            panels.extend([img_a, img_b, img_c])
            
        return panels, "Please fill in the missing cell by combining the shapes."