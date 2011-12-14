#!/usr/bin/env python
# coding: utf-8

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def publish():
    """
    Publish this package to PyPI (aka "the Cheeseshop").

    """
    os.system('python setup.py sdist upload')


def make_long_description():
    """
    Return the long description for the package.

    """
    long_description = open('README.rst').read() + '\n\n' + open('HISTORY.rst').read()

    return long_description


if sys.argv[-1] == 'publish':
    publish()
    sys.exit()

long_description = make_long_description()

setup(name='pystache',
      version='0.3.1',
      description='Mustache for Python',
      long_description=long_description,
      author='Chris Wanstrath',
      author_email='chris@ozmm.org',
      url='http://github.com/defunkt/pystache',
      packages=['pystache'],
      license='MIT',
      entry_points = {
        'console_scripts': ['pystache=pystache.commands:main'],
      },
      classifiers = (
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
      )
)

