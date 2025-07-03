#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="omni-bot",
    version="1.0.0",
    author="Alexander Alekseev",
    author_email="phghost@mail.ru",
    description="Text bot with different text providers",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/Korean-DOG/omni-bot",
    license="Apache-2.0 license",
    packages=find_packages(exclude=["unit_test.py"]),
    install_requires=open("requirements.txt").read().split("\n")
)
