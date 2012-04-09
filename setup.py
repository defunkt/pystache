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
    import setuptools as dist
except ImportError:
    from distutils import core as dist

# TODO: use the logging module instead.
print("Using: version %s of %s" % (repr(dist.__version__), repr(dist)))
setup = dist.setup


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

# We follow the guidance here for compatibility with using setuptools instead
# of Distribute under Python 2 (on the subject of new, unrecognized keyword
# arguments to setup()):
#
#   http://packages.python.org/distribute/python3.html#note-on-compatibility-with-setuptools
#
if sys.version_info < (3, ):
    extra = {}
else:
    extra = {
        # Causes 2to3 to be run during the build step.
        'use_2to3': True,
        'convert_2to3_doctests': ['README.rst'],
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
      packages=dist.find_packages(),
      package_data = {
          # Include the README so doctests can be run.
          # TODO: is there a better way to include the README?
          'pystache': [
              '../README.rst',
              '../ext/spec/specs/*.json',
              '../ext/spec/specs/*.yml',
          ],
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
      ),
      **extra
)
