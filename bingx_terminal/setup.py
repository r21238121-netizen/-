"""
Setup script for BingX Local AI Trading Terminal
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="bingx-ai-terminal",
    version="1.0.0",
    author="Trading Bot Developer",
    author_email="developer@example.com",
    description="A local AI trading terminal for BingX futures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bingx-ai-terminal",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "bingx-terminal=src.main:main",
        ],
    },
)