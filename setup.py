"""
Setup script for Smart HVAC Control System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="smart-hvac-control",
    version="1.0.0",
    author="HVAC Control Team",
    author_email="team@hvaccontrol.com",
    description="Intelligent HVAC control system with IoT monitoring and multiple control strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hvacteam/smart-hvac-control",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=1.0",
        ],
        "docs": [
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hvac-control=main:main",
            "hvac-dashboard=iot.dashboard:main",
            "hvac-simulation=simulation.thermal_model:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md", "*.txt"],
    },
    project_urls={
        "Bug Reports": "https://github.com/hvacteam/smart-hvac-control/issues",
        "Source": "https://github.com/hvacteam/smart-hvac-control",
        "Documentation": "https://smart-hvac-control.readthedocs.io/",
    },
)