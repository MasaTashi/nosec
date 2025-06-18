#!/usr/bin/env python3
"""
Setup script for Academic Verifier.
"""

from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="academic_verifier",
    version="0.1.0",
    description="A tool for detecting AI-generated content, hallucinations, and misunderstandings in academic papers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Academic Verifier Team",
    author_email="info@example.com",
    url="https://github.com/yourusername/academic-verifier",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "academic-verifier=src.main:main",
        ],
    },
)