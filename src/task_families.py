# src/task_families.py

import io
import random
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

# --- Configuration for the Task ---

# Define the standard image size we'll be working with.
IMAGE_SIZE = (384, 384)

# Define the possible shapes and colors for the points.
POINT_COLORS = ['red', 'blue', 'green', 'black', 'purple', 'orange']
POINT_SHAPES = {
    'circles': 'o',
    'squares': 's',
    'triangles': '^',
    'stars': '*',
    'diamonds': 'D'
}

# --- Helper Functions ---

def format_number(n):
    """
    Formats a number to the nearest hundredth, removing unnecessary trailing zeros.
    Example: 2.30 -> '2.3', 5.00 -> '5', 1.25 -> '1.25'
    """
    return ('%.2f' % n).rstrip('0').rstrip('.')

def fig_to_pil(fig):
    """Converts a Matplotlib figure to a PIL Image."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    img = Image.open(buf).convert('RGB')
    return img

def create_base_grid(axis_limit, spine_style, grid_scale):
    """
    Creates a Matplotlib figure with a minimal grid.

    Args:
        axis_limit (float): The value 'a' for setting axis limits from -a to a.
        spine_style (str): Style for the axis spines ('dotted', 'dashed', 'solid').
        grid_scale (float): The percentage of the image the grid should occupy (0.5 to 1.0).

    Returns:
        A tuple of (matplotlib.figure.Figure, matplotlib.axes.Axes).
    """
    fig, ax = plt.subplots(figsize=(4, 4), dpi=IMAGE_SIZE[0] / 4)

    # Set axis limits
    ax.set_xlim(-axis_limit, axis_limit)
    ax.set_ylim(-axis_limit, axis_limit)

    # Set minimal labels
    ax.set_xlabel('x', fontsize=10)
    ax.set_ylabel('y', fontsize=10)
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.set_aspect('equal', adjustable='box')

    # Style spines
    for spine in ax.spines.values():
        spine.set_linestyle(spine_style)
        spine.set_color('gray')

    # Remove top and right spines for a cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Adjust the plot size within the figure
    fig.subplots_adjust(
        left=(1 - grid_scale) / 2,
        right=1 - (1 - grid_scale) / 2,
        bottom=(1 - grid_scale) / 2,
        top=1 - (1 - grid_scale) / 2
    )
    
    return fig, ax

# --- Main Task Generation Function ---

def generate_plot_points_task(difficulty=0.5):
    """
    Generates a single sample for the "plot points on a plane" task.

    The task provides a text prompt with points and an image of an empty grid.
    The target is a blank text prompt and the same grid with the points plotted.

    Args:
        difficulty (float): A value from 0.0 to 1.0. (Not used yet, but good practice).

    Returns:
        dict: A dictionary containing the input/output image and text.
              Keys: 'input_image', 'input_text', 'output_image', 'output_text'.
    """
    # 1. Generate random points
    num_points = random.randint(2, 8)
    points = np.random.uniform(-5.0, 5.0, size=(num_points, 2))

    # 2. Determine point style (optional)
    use_custom_style = random.choice([True, False])
    if use_custom_style:
        color_name = random.choice(POINT_COLORS)
        shape_name = random.choice(list(POINT_SHAPES.keys()))
        marker = POINT_SHAPES[shape_name]
    else:
        # Default style if not specified
        color_name = 'blue'
        shape_name = 'circles'
        marker = 'o'

    # 3. Formulate the input text
    prompt = "Please plot the following points on the plane: "
    point_strs = [f"({format_number(p[0])}, {format_number(p[1])})" for p in points]
    prompt += ", ".join(point_strs)
    
    if use_custom_style:
        prompt += f" as {color_name} {shape_name}."
    else:
        prompt += "."
    
    # 4. Determine grid parameters
    max_abs_val = np.max(np.abs(points))
    axis_limit = 1.1 * max_abs_val
    spine_style = random.choice(['dotted', 'dashed', 'solid'])
    grid_scale = random.uniform(0.5, 1.0)

    # 5. Generate the input image (empty grid)
    input_fig, input_ax = create_base_grid(axis_limit, spine_style, grid_scale)
    input_image = fig_to_pil(input_fig)
    plt.close(input_fig) # Close the figure to free up memory

    # 6. Generate the output image (grid with points)
    output_fig, output_ax = create_base_grid(axis_limit, spine_style, grid_scale)
    output_ax.scatter(points[:, 0], points[:, 1], c=color_name, marker=marker, s=50) # s is size
    output_image = fig_to_pil(output_fig)
    plt.close(output_fig)

    return {
        'input_image': input_image,
        'input_text': prompt,
        'output_image': output_image,
        'output_text': "" # Output text is blank as requested
    }

def list_available_tasks():
    """Returns a list of the task-generating functions available in this module."""
    return ['plot_points']

if __name__ == '__main__':
    # --- Example Usage: Generate and save one sample ---
    print("Generating a sample for the 'plot_points' task...")
    sample = generate_plot_points_task()

    print("\n--- Input ---")
    print(f"Text: {sample['input_text']}")
    print(f"Image Size: {sample['input_image'].size}")

    print("\n--- Output ---")
    print(f"Text: '{sample['output_text']}'")
    print(f"Image Size: {sample['output_image'].size}")

    # Save the images to disk to check them
    sample['input_image'].save("sample_input.png")
    sample['output_image'].save("sample_output.png")

    print("\nSaved 'sample_input.png' and 'sample_output.png' in the current directory.")