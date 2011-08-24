#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def publish():
    """Publishes module to The Cheeseshop."""

    os.system('python setup.py sdist upload')


if 'publish' in sys.argv:
    publish()
    sys.exit()


setup(
    name='pystache',
    version='0.3.1',
    description='Mustache for Python',
    long_description=open('README.rst').read() + '\n\n' + open('HISTORY.rst').read(),
    author='Chris Wanstrath',
    author_email='chris@ozmm.org',
    url='http://github.com/defunkt/pystache',
    packages=['pystache'],
    license='MIT',
    classifiers = (
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6"
    )
)

