from setuptools import setup, find_packages
from os import path

setup(
    name='machinacli',
    version='0.1',
    description='Machina CLI',
    author='',
    author_email='behren2@protonmail.com',
    keywords='machina',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['pika'],
    scripts=['bin/machinacli.py']
)
