#!/usr/bin/env python
# coding: utf-8

"""
This script supports publishing Pystache to PyPI.

This docstring contains instructions to Pystache maintainers on how
to release a new version of Pystache.

(1) Push to PyPI.  To release a new version of Pystache to PyPI--

    http://pypi.python.org/pypi/pystache

create a PyPI user account if you do not already have one.  The user account
will need permissions to push to PyPI.  A current "Package Index Owner" of
Pystache can grant you those permissions.

When you have permissions, run the following (after preparing the release,
merging to master, bumping the version number in setup.py, etc):

    python setup.py publish

If you get an error like the following--

    Upload failed (401): You must be identified to edit package information

then add a file called .pyirc to your home directory with the following
contents:

    [server-login]
    username: <PyPI username>
    password: <PyPI password>

as described here, for example:

    http://docs.python.org/release/2.5.2/dist/pypirc.html

(2) Tag the release on GitHub.  Here are some commands for tagging.

List current tags:

    git tag -l -n3

Create an annotated tag:

    git tag -a -m "Version 0.5.1" "v0.5.1"

Push a tag to GitHub:

    git push --tags defunkt v0.5.1

"""

import os
import sys

py_version = sys.version_info

# Distribute works with Python 2.3.5 and above:
#   http://packages.python.org/distribute/setuptools.html#building-and-distributing-packages-with-distribute
if py_version < (2, 3, 5):
    # TODO: this might not work yet.
    import distutils as dist
    from distutils import core
    setup = core.setup
else:
    import setuptools as dist
    setup = dist.setup

# TODO: use the logging module instead of printing.
# TODO: include the following in a verbose mode.
# print("Using: version %s of %s" % (repr(dist.__version__), repr(dist)))


VERSION = '0.5.2'  # Also change in pystache/__init__.py.

HISTORY_PATH = 'HISTORY.rst'
LICENSE_PATH = 'LICENSE'
README_PATH = 'README.rst'

CLASSIFIERS = (
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.4',
    'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.1',
    'Programming Language :: Python :: 3.2',
)


def read(path):
    """
    Read and return the contents of a text file as a unicode string.

    """
    # This function implementation was chosen to be compatible across Python 2/3.
    f = open(path, 'rb')
    # We avoid use of the with keyword for Python 2.4 support.
    try:
        b = f.read()
    finally:
        f.close()

    return b.decode('utf-8')


def publish():
    """
    Publish this package to PyPI (aka "the Cheeseshop").

    """
    os.system('python setup.py sdist upload')


def make_long_description():
    """
    Return the long description for the package.

    """
    license = """\
License
=======

""" + read(LICENSE_PATH)

    sections = [read(README_PATH), read(HISTORY_PATH), license]
    return '\n\n'.join(sections)


if sys.argv[-1] == 'publish':
    publish()
    sys.exit()

# We follow the guidance here for compatibility with using setuptools instead
# of Distribute under Python 2 (on the subject of new, unrecognized keyword
# arguments to setup()):
#
#   http://packages.python.org/distribute/python3.html#note-on-compatibility-with-setuptools
#
if py_version < (3, ):
    extra = {}
else:
    extra = {
        # Causes 2to3 to be run during the build step.
        'use_2to3': True,
    }

# We use the package simplejson for older Python versions since Python
# does not contain the module json before 2.6:
#
#   http://docs.python.org/library/json.html
#
# Moreover, simplejson stopped officially support for Python 2.4 in version 2.1.0:
#
#   https://github.com/simplejson/simplejson/blob/master/CHANGES.txt
#
requires = []
if py_version < (2, 5):
    requires.append('simplejson<2.1')
elif py_version < (2, 6):
    requires.append('simplejson')

INSTALL_REQUIRES = requires

# TODO: decide whether to use find_packages() instead.  I'm not sure that
#   find_packages() is available with distutils, for example.
PACKAGES = [
    'pystache',
    'pystache.commands',
    # The following packages are only for testing.
    'pystache.tests',
    'pystache.tests.data',
    'pystache.tests.data.locator',
    'pystache.tests.examples',
]


def main(sys_argv):

    long_description = make_long_description()
    template_files = ['*.mustache', '*.txt']

    setup(name='pystache',
          version=VERSION,
          license='MIT',
          description='Mustache for Python',
          long_description=long_description,
          author='Chris Wanstrath',
          author_email='chris@ozmm.org',
          maintainer='Chris Jerdonek',
          url='http://github.com/defunkt/pystache',
          install_requires=INSTALL_REQUIRES,
          packages=PACKAGES,
          package_data = {
              # Include template files so tests can be run.
              'pystache.tests.data': template_files,
              'pystache.tests.data.locator': template_files,
              'pystache.tests.examples': template_files,
          },
          entry_points = {
            'console_scripts': [
                'pystache=pystache.commands.render:main',
                'pystache-test=pystache.commands.test:main',
            ],
          },
          classifiers = CLASSIFIERS,
          **extra
    )


if __name__=='__main__':
    main(sys.argv)
