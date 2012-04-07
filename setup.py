#!/usr/bin/env python
# coding: utf-8

"""
This script supports installing and distributing pystache.

Below are instructions to pystache maintainers on how to push a new
version of pystache to PyPI--

    http://pypi.python.org/pypi/pystache

Create a PyPI user account.  The user account will need permissions to push
to PyPI.  A current "Package Index Owner" of pystache can grant you those
permissions.

When you have permissions, run the following (after preparing the release,
bumping the version number in setup.py, etc):

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
    from setuptools import setup, find_packages
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
template_files = ['*.mustache', '*.txt']

# We follow the suggestion here for compatibility with earlier versions
# of Python:
#
#   http://packages.python.org/distribute/python3.html#note-on-compatibility-with-setuptools
#
if sys.version_info < (3, ):
    extra = {}
else:
    # For testing purposes, we also use use_2to3 with Python 2.7.  This
    # lets us troubleshoot the absence of package resources in the build
    # directory more easily (e.g. the absence of README.rst), since we can
    # troubleshoot it while using Python 2.7 instead of Python 3.
    extra = {
        'use_2to3': True,
    }

setup(name='pystache',
      version='0.5.0-rc',
      license='MIT',
      description='Mustache for Python',
      long_description=long_description,
      author='Chris Wanstrath',
      author_email='chris@ozmm.org',
      maintainer='Chris Jerdonek',
      url='http://github.com/defunkt/pystache',
      packages=find_packages(),
      package_data = {
          # Include template files so tests can be run.
          'examples': template_files,
          'pystache.tests.data': template_files,
          'pystache.tests.data.locator': template_files,
      },
      test_suite='pystache.tests',
      entry_points = {
        'console_scripts': ['pystache=pystache.commands:main'],
      },
      classifiers = (
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
      ),
      **extra
)
