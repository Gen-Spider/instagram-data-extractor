#!/usr/bin/env python3
"""Setup script for Instagram Data Extractor."""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="instagram-data-extractor",
    version="1.0.0",
    author="Git-Spider", 
    author_email="noreply@github.com",
    description="A Python-based Instagram data extraction tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Gen-Spider/instagram-data-extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10", 
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "instagram-extractor=instagram_extractor:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/Gen-Spider/instagram-data-extractor/issues",
        "Source": "https://github.com/Gen-Spider/instagram-data-extractor",
        "Documentation": "https://github.com/Gen-Spider/instagram-data-extractor#readme",
    },
)