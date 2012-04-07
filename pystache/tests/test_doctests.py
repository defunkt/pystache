# coding: utf-8

"""
Creates unittest.TestSuite instances for the doctests in the project.

"""

# This module follows the guidance documented here:
#
#   http://docs.python.org/library/doctest.html#unittest-api
#

import os
import doctest
import unittest

import pystache
from pystache.tests.common import PROJECT_DIR


# The paths to text files (i.e. non-module files) containing doctests.
# Paths should be OS-specific and relative to the project directory.
text_file_paths = ['README.rst']


def load_tests(loader, tests, ignore):
    # Since module_relative is False in our calls to DocFileSuite below,
    # paths should be OS-specific.  Moreover, we choose absolute paths
    # so that the current working directory does not come into play.
    # See the following for more info--
    #
    #   http://docs.python.org/library/doctest.html#doctest.DocFileSuite
    #
    paths = [os.path.join(PROJECT_DIR, path) for path in text_file_paths]
    tests.addTests(doctest.DocFileSuite(*paths, module_relative=False))

    return tests
