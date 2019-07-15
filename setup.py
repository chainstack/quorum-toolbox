#!/usr/bin/env python3

from pathlib import Path

from setuptools import setup, find_packages


def read(fname):
    return open(str(Path(__file__).parent / Path(fname))).read()


setup(name='quorumtoolbox',
      version='2.1.0',
      description='Quorum-toolbox (supports Raft and Ibft)',
      long_description=read('README.md'),
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
          'requests>=2.20.0',
          'sh>=1.12.14',
          'psutil>=5.4.8',
      ],
      )
