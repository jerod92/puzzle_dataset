# dataset.py
import torch
from torch.utils.data import Dataset
import numpy as np
import random
from PIL import Image
import torchvision

# Import all puzzle generator classes
from puzzles.sudoku import SudokuPuzzle
from puzzles.algebra import AlgebraPuzzle
from puzzles.graph import GraphPuzzle
from puzzles.arithmetic import ArithmeticPuzzle
from puzzles.maze import MazePuzzle
from puzzles.shape_augmentation import ShapeAugmentationPuzzle
from puzzles.line_drawing import LineDrawingPuzzle
from puzzles.tictactoe import TicTacToePuzzle
from puzzles.tangent_line import TangentLinePuzzle
from puzzles.inscribed_circle import InscribedCirclePuzzle
from puzzles.move_to_target import MoveToTargetPuzzle
from puzzles.jigsaw_puzzle import JigsawPuzzle
from puzzles.color_grid import ColorGridPuzzle
from puzzles.object_counting import ObjectCountingPuzzle
from puzzles.matrix_puzzles import (
    RotationMatrixPuzzle,
    FillProgressionMatrixPuzzle,
    MonochromeLogicMatrixPuzzle,
    TricolorRotationMatrixPuzzle,
    LatinSquareMatrixPuzzle,
    ShapeSuperpositionMatrixPuzzle
)

class InterleavedPuzzleDataset(Dataset):
    """
    Generates a dataset of interleaved puzzles by delegating to modular puzzle generator classes.
    """
    def __init__(self, puzzle_counts, sudoku_df=None, img_size=384):
        self.img_size = img_size
        self.puzzle_manifest = []

        caltech_dataset = None
        if 'jigsaw_puzzle' in puzzle_counts and puzzle_counts['jigsaw_puzzle'] > 0:
            print("Jigsaw puzzle requested, loading Caltech256 dataset...")
            # This will download the dataset on the first run to a './data' folder
            caltech_dataset = torchvision.datasets.Caltech256(root='./data', download=True)
            print("Caltech256 dataset loaded.")
            
        # Mapping of puzzle type names to their generator classes
        self.puzzle_generators = {
            'algebra': AlgebraPuzzle(img_size),
            'graph': GraphPuzzle(img_size),
            'arithmetic': ArithmeticPuzzle(img_size),
            'maze': MazePuzzle(img_size),
            'shape_augmentation': ShapeAugmentationPuzzle(img_size),
            'line_drawing': LineDrawingPuzzle(img_size),
            'tictactoe': TicTacToePuzzle(img_size),
            'rotation_matrix': RotationMatrixPuzzle(img_size),
            'fill_progression_matrix': FillProgressionMatrixPuzzle(img_size),
            'monochrome_logic_matrix': MonochromeLogicMatrixPuzzle(img_size),
            'tricolor_rotation_matrix': TricolorRotationMatrixPuzzle(img_size),
            'latin_square_matrix': LatinSquareMatrixPuzzle(img_size),
            'shape_superposition_matrix': ShapeSuperpositionMatrixPuzzle(img_size),
            'tangent_line': TangentLinePuzzle(img_size),
            'inscribed_circle': InscribedCirclePuzzle(img_size),
            'move_to_target': MoveToTargetPuzzle(img_size),
            'jigsaw_puzzle': JigsawPuzzle(img_size, image_dataset=caltech_dataset), # Pass dataset here
            'color_grid': ColorGridPuzzle(img_size),
            'object_counting': ObjectCountingPuzzle(img_size),
        }
        
        # Sudoku has special data requirements
        if 'sudoku' in puzzle_counts and sudoku_df is not None:
             self.puzzle_generators['sudoku'] = SudokuPuzzle(img_size)

        for puzzle_type, count in puzzle_counts.items():
            if puzzle_type == 'sudoku':
                if sudoku_df is not None and count > 0:
                    for _, row in sudoku_df.sample(n=count, replace=True).iterrows():
                        # Pass the specific sudoku data to the manifest
                        self.puzzle_manifest.append(('sudoku', (row['quizzes'], row['solutions'])))
            elif puzzle_type in self.puzzle_generators:
                self.puzzle_manifest.extend([(puzzle_type, None)] * count)

        random.shuffle(self.puzzle_manifest)

    def __len__(self):
        return len(self.puzzle_manifest)

    def __getitem__(self, idx):
        puzzle_type, data = self.puzzle_manifest[idx]

        generator = self.puzzle_generators[puzzle_type]
        
        if puzzle_type == 'sudoku':
            # Sudoku generator needs the specific puzzle strings
            input_image, target_image, text_description = generator.generate(data)
        else:
            # All other generators are called without arguments
            input_image, target_image, text_description = generator.generate()

        return self._to_tensor(input_image), self._to_tensor(target_image), text_description

    def _to_tensor(self, img):
        """Converts a PIL image to a PyTorch tensor."""
        return (torch.from_numpy(np.array(img)).permute(2, 0, 1).float() / 127.5) - 1
