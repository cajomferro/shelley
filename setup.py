# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='shelley',
    version='0.1.0',
    description='Shelley checker',
    long_description=readme,
    author='Carlos MaoDeFerro',
    url='https://bitbucket.org/safeiot/shelley-checker/',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)