from setuptools import setup, find_packages
from os import path

setup(
    name='machina',
    version='0.1',
    description='A scalable APK analysis pipeline',
    author='',
    author_email='behren2@protonmail.com',
    keywords='machina',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    python_requires='>=3.5',
    install_requires=['pika'],
    include_package_data = True,
)
