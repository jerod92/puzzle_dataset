from setuptools import setup, find_packages

setup(
    name="procedural_dataset",
    version="0.1.0",
    description="A procedurally generated dataset for vision-language tasks.",
    author="Your Name", # Change this to your name
    author_email="your.email@example.com", # Change this to your email
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "Pillow",
        "torch",
        "torchvision",
    ],
)