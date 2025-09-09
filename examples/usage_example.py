# examples/usage_example.py

import torch
from torch.utils.data import DataLoader
# The following imports are placeholders for the classes you will create
from src.dataset_generator import Generator # Main class
from src.task_families import list_available_tasks # A helper function

def main():
    """
    An example demonstrating how to generate and use a dataset.
    """
    print("Welcome to the Procedurally Generated Dataset example!")

    # --- 1. Configuration ---
    dataset_size = 1000
    difficulty_level = 0.5 # 0.0 = easiest, 1.0 = hardest
    batch_size = 32

    # Let's see what tasks are available (this function will be in task_families.py)
    available_tasks = list_available_tasks()
    print(f"Available task families: {available_tasks}")

    # Select the tasks you want to include in your dataset
    selected_tasks = ['shape_identification', 'color_counting', 'symbol_matching']

    # --- 2. Initialize the Generator ---
    print("\nInitializing dataset generator...")
    generator = Generator(task_families=selected_tasks)

    # --- 3. Generate the Dataset ---
    print(f"Generating a dataset of size {dataset_size} with difficulty {difficulty_level}...")
    # The generate() method will return a PyTorch-compatible Dataset object
    procedural_dataset = generator.generate(
        dataset_size=dataset_size,
        difficulty=difficulty_level
    )
    print("Dataset generation complete!")
    print(f"Total samples in dataset: {len(procedural_dataset)}")

    # --- 4. Use the Dataset with a PyTorch DataLoader ---
    # The dataset can be directly wrapped by a DataLoader for training.
    data_loader = DataLoader(
        dataset=procedural_dataset,
        batch_size=batch_size,
        shuffle=True
    )

    # --- 5. Inspect a Sample Batch ---
    # Retrieve one batch of data to see its structure.
    print("\nInspecting a sample batch from the DataLoader...")
    first_batch = next(iter(data_loader))

    # The exact structure will depend on your implementation,
    # but it will follow the (image, text) format.
    input_images, input_texts, output_images, output_texts = first_batch

    print(f"Input images batch shape: {input_images.shape}")
    print(f"Input texts in batch: {len(input_texts)}")
    print(f"  - Example text: '{input_texts[0]}'")

    print(f"Output images batch shape: {output_images.shape}")
    print(f"Output texts in batch: {len(output_texts)}")
    print(f"  - Example text: '{output_texts[0]}'")


if __name__ == "__main__":
    main()