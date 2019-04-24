"""Module for installing the presentation package."""
from setuptools import setup, find_packages

setup(
    name="azure_ml_tutorial",
    packages=find_packages(),
    version="0.1.0",
    description="This package contains helper code to go along with the North Texas AI meetup presented April 24th, 2019 by CBRE's Host ML Team.",  # noqa
)
