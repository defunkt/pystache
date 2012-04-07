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
import pkgutil
import unittest

import pystache
from pystache.tests.common import PROJECT_DIR, SOURCE_DIR


# The paths to text files (i.e. non-module files) containing doctests.
# Paths should be OS-specific and relative to the project directory.
text_file_paths = ['README.rst']


# The following load_tests() function implements unittests's load_tests
# protocol added in Python 2.7:
#
#   http://docs.python.org/library/unittest.html#load-tests-protocol
#
# Using this protocol lets us include the doctests in test runs without
# using nose, for example when using Distribute's test as in the following:
#
#     python setup.py test
#
# TODO: find a substitute for the load_tests protocol for Python versions
#   before version 2.7.
#
# HACK: Allowing load_tests() to be called without arguments is a hack
# to allow unit tests to be run with nose's nosetests without error.
# Otherwise, nose interprets the following function as a test case,
# raising the following error:
#
#   TypeError: load_tests() takes exactly 3 arguments (0 given)
#
def load_tests(loader=None, tests=None, ignore=None):
    if loader is None:
        return
    # Since module_relative is False in our calls to DocFileSuite below,
    # paths should be OS-specific.  Moreover, we choose absolute paths
    # so that the current working directory does not come into play.
    # See the following for more info--
    #
    #   http://docs.python.org/library/doctest.html#doctest.DocFileSuite
    #
    paths = [os.path.join(PROJECT_DIR, path) for path in text_file_paths]
    tests.addTests(doctest.DocFileSuite(*paths, module_relative=False))

    modules = get_module_doctests()
    for module in modules:
        suite = doctest.DocTestSuite(module)
        tests.addTests(suite)

    return tests


def get_module_doctests():
    modules = []

    for pkg in pkgutil.walk_packages([SOURCE_DIR]):
        # The importer is a pkgutil.ImpImporter instance:
        #
        #   http://docs.python.org/library/pkgutil.html#pkgutil.ImpImporter
        #
        importer, module_name, is_package = pkg
        if is_package:
            # Otherwise, we will get the following error when adding tests:
            #
            #   ValueError: (<module 'tests' from '.../pystache/tests/__init__.pyc'>, 'has no tests')
            #
            continue
        # The loader is a pkgutil.ImpLoader instance.
        loader = importer.find_module(module_name)
        module = loader.load_module(module_name)
        modules.append(module)

    return modules
