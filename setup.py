# setup.py
from setuptools import setup, find_packages

setup(
    name="minigo",
    version="0.1",
    package_dir={"": "MiniGo/src"},
    packages=find_packages(where="MiniGo/src"),
    install_requires=[
        # Add dependencies here if any
    ],
    python_requires=">=3.10",
)