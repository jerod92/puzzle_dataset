# Procedurally Generated Multimodal Puzzle Dataset

This project is a Python-based framework for creating procedurally generated datasets focused on shapes, colors, and symbols. The goal is to produce datasets for multimodal (image + text) machine learning tasks with customizable difficulty and size.

## Features

- **Procedural Generation**: Create vast amounts of training data without manual labeling.
- **Multimodal Format**: Each sample consists of (image + text) inputs and (image + text) outputs.
- **Task-Focused**: The generation logic is centered around elemental tasks involving shapes, colors, and symbols.
- **Customizable**: Easily control the difficulty, size, and task variety of the generated dataset.
- **PyTorch-Ready**: Outputs a `torch.utils.data.Dataset` object, ready for immediate use in training pipelines.

## Folder Structure