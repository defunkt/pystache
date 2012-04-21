# coding: utf-8

"""
Allows all tests to be run.

This module is for our test console script.

"""

import os
import sys
from unittest import TestProgram

from pystache.tests.common import PACKAGE_DIR
from pystache.tests.doctesting import get_module_doctests


UNITTEST_FILE_PREFIX = "test_"

# TODO: enhance this to work with doctests (instead of using the load_tests
#   protocol), etc.

# Notes for TODO:
#
# The function unittest.main() is an alias for unittest.TestProgram's
# constructor.  The constructor calls self.runTests() as its final step, which
# expects self.test to be set.  The constructor sets the self.test attribute
# by calling one of self.testLoader's "loadTests" methods.  These methods
# return a unittest.TestSuite instance.  Thus, self.test is set to a TestSuite
# instance prior to calling runTests().
#
# Our strategy is to subclass unittest.TestProgram and override its runTests()
# method.  Our implementation of runTests() will add to self.test additional
# TestCase or TestSuite instances (e.g. doctests and spec tests), and then
# call the base class's runTests().

def _find_unittest_files(package_dir):
    """
    Return a list of paths to all unit-test files in the given package directory.

    """
    paths = []  # Return value.

    def is_unittest(file_name):
        return file_name.startswith(UNITTEST_FILE_PREFIX) and file_name.endswith('.py')

    # os.walk() is new in Python 2.3
    #   http://docs.python.org/library/os.html#os.walk
    for dir_path, dir_names, file_names in os.walk(package_dir):
        file_names = filter(is_unittest, file_names)

        for file_name in file_names:
            path = os.path.join(dir_path, file_name)
            paths.append(path)

    return paths


def _get_module_names(package_dir, paths):
    """
    Return a list of fully-qualified test module names given a list of module paths.

    """
    package_dir = os.path.abspath(package_dir)
    package_name = os.path.split(package_dir)[1]

    prefix_length = len(package_dir)

    module_names = []
    for path in paths:
        path = os.path.abspath(path)  # for example <path_to_package>/subpackage/module.py
        rel_path = path[prefix_length:]  # for example /subpackage/module.py
        rel_path = os.path.splitext(rel_path)[0]  # for example /subpackage/module

        parts = []
        while True:
            (rel_path, tail) = os.path.split(rel_path)
            if not tail:
                break
            parts.insert(0, tail)
        # We now have, for example, ['subpackage', 'module'].
        parts.insert(0, package_name)
        module = ".".join(parts)
        module_names.append(module)

    return module_names


def _get_test_module_names(package_dir):
    """
    Return a list of fully-qualified module names given a list of module paths.

    """
    paths = _find_unittest_files(package_dir)
    modules = _get_module_names(package_dir, paths)

    return modules

def _discover_test_modules(package_dir):
    """
    Discover and return a sorted list of the names of unit-test modules.

    """
    modules = _get_test_module_names(package_dir)
    modules.sort()

    # This is a sanity check to ensure that the unit-test discovery
    # methods are working.
    if len(modules) < 1:
        raise Exception("No unit-test modules found.")

    return modules



class _PystacheTestProgram(TestProgram):

    """
    Instantiating an instance of this class runs all tests.

    """

    def runTests(self):
        doctest_suites = get_module_doctests()
        self.test.addTests(doctest_suites)

        TestProgram.runTests(self)


class TestHarness(object):

    """
    Discovers and runs unit tests.

    """

    def run_tests(self, sys_argv):
        """
        Run all unit tests inside the given package.

        Arguments:

          sys_argv: a reference to sys.argv.

        """
        if len(sys_argv) <= 1 or sys_argv[-1].startswith("-"):
            # Then no explicit module or test names were provided, so
            # auto-detect all unit tests.
            module_names = _discover_test_modules(PACKAGE_DIR)
            sys_argv.extend(module_names)

        # We pass None for the module because we do not want the unittest
        # module to resolve module names relative to a given module.
        # (This would require importing all of the unittest modules from
        # this module.)  See the loadTestsFromName() method of the
        # unittest.TestLoader class for more details on this parameter.
        _PystacheTestProgram(argv=sys_argv, module=None)
        # No need to return since unitttest.main() exits.
