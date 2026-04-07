"""
Setup configuration for uk-geo-neighbors package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="uk-geo-neighbors",
    version="0.1.0",
    author="Samuel Bakst",
    author_email="107sbakst@gmail.com",
    description="Python package for finding neighboring UK administrative areas using geopandas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/107SBakst/geo-functions",
    project_urls={
        "Bug Tracker": "https://github.com/107SBakst/geo-functions/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research", 
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "geopandas>=0.10.0",
        "pandas>=1.3.0",
        "shapely>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    keywords="geopandas, uk, administrative areas, neighbors, boundaries, geography, spatial analysis",
)