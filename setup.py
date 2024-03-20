import os
from setuptools import setup

#Read the dependencies from the requirements.txt file
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name = 'PANACEA',
    version='1.0',
    packages = [],
    install_requires = [requirements],
    entry_points = {},
    python_requires = '>=3.6'
)

