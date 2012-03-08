#!/usr/bin/env python
# coding: utf-8

"""
To push a new version of pystache to PyPI--

    http://pypi.python.org/pypi/pystache

you first need to be added as a "Package Index Owner" of pystache.

Then run the following (after preparing the release, bumping the version
number, etc):

    > python setup.py publish

If you get an error like the following--

    Upload failed (401): You must be identified to edit package information

then add a file called .pyirc to your home directory with the following
contents:

    [server-login]
    username: <PyPI username>
    password: <PyPI password>

as described here, for example:

    http://docs.python.org/release/2.5.2/dist/pypirc.html

"""

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
      version='0.4.0',
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

