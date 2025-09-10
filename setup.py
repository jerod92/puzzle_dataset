# setup.py

from setuptools import setup, find_packages

# Read the contents of your README file
# This will be used as the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the requirements from the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="puzzle_generator",
    version="0.1.0",
    author="Your Name",  # <--- Change this
    author_email="your.email@example.com",  # <--- Change this
    description="A modular data generator for a variety of visual puzzles.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your_username/your_repo_name",  # <--- Change this to your repo URL
    
    # find_packages() automatically discovers the 'puzzles' and 'utils' directories
    # because they contain an __init__.py file.
    packages=find_packages(),
    
    # This list of dependencies will be installed when someone runs 'pip install'
    install_requires=requirements,
    
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        
        # Specify the license
        "License :: OSI Approved :: MIT License", # Or another license you prefer
        
        # Specify the Python versions you support
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)