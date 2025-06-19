"""
Setuptools configuration for Aufmass-App.
"""
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from setuptools import setup, find_packages

setup(
    name="aufmass_app",
    version="0.1.0",
    description="Eine Anwendung zur Verwaltung von Aufmaßarbeiten",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.0.0",
        # Add other dependencies here
    ],
    entry_points={
        'console_scripts': [
            'aufmass-app=aufmass_app.app:main',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
