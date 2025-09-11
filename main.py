# main.py
import pandas as pd
from torch.utils.data import DataLoader
from dataset import InterleavedPuzzleDataset

def main():
    """
    An example of how to use the InterleavedPuzzleDataset.
    """
    # --- Configuration ---
    IMG_SIZE = 384
    BATCH_SIZE = 4

    # Define how many of each puzzle type you want
    puzzle_counts = {
        'sudoku': 10,
        'maze': 10,
        'algebra': 5,
        'graph': 5,
        'arithmetic': 5,
        'shape_augmentation': 8,
        'line_drawing': 5,
        'tictactoe': 8,
        'rotation_matrix': 5,
        'fill_progression_matrix': 5,
        'monochrome_logic_matrix': 5,
        'tricolor_rotation_matrix': 5,
        'latin_square_matrix': 5,
        'shape_superposition_matrix': 5,
        'tangent_line': 4,
        'inscribed_circle': 4,
        'move_to_target': 4,
        #'jigsaw_puzzle': 4, # Make sure you have images in the jigsaw_images folder!
        'color_grid': 4,
        'object_counting': 5,
        'vector_logic': 8,
        'matrix_multiplication': 4,
        'one_d_measuring': 6,
        'two_d_measuring': 6,
    }

    # --- Load Sudoku Data from CSV ---
    try:
        sudoku_df = pd.read_csv('sudoku_10000.csv')
        print("Successfully loaded sudoku_10000.csv")
    except FileNotFoundError:
        print("Error: sudoku_10000.csv not found. Sudoku puzzles will be skipped.")
        sudoku_df = None


    # --- Create Dataset and DataLoader ---
    print("Initializing dataset...")
    dataset = InterleavedPuzzleDataset(
        puzzle_counts=puzzle_counts,
        sudoku_df=sudoku_df,
        img_size=IMG_SIZE
    )

    data_loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=True
    )

    print(f"Dataset created with {len(dataset)} samples.")
    if len(dataset) == 0:
        print("Dataset is empty. Check your puzzle counts and data files.")
        return

    # --- Iterate and Display Info ---
    # Fetch one batch from the data loader
    input_images, target_images, descriptions = next(iter(data_loader))

    print(f"\nFetched one batch of size {len(descriptions)}.")
    print(f"Input image tensor shape: {input_images.shape}")
    print(f"Target image tensor shape: {target_images.shape}")
    print("\nText descriptions for this batch:")
    for i, desc in enumerate(descriptions):
        print(f"  {i+1}: {desc}")
        
    # To save the images from the first batch for verification:
    # from torchvision.utils import save_image, make_grid
    # # Normalize from [-1, 1] to [0, 1] for saving
    # input_grid = make_grid((input_images + 1) / 2)
    # target_grid = make_grid((target_images + 1) / 2)
    # save_image(input_grid, 'input_batch.png')
    # save_image(target_grid, 'target_batch.png')
    # print("\nSaved image grids to input_batch.png and target_batch.png")


if __name__ == '__main__':
    main()
