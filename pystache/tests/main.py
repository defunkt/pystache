# coding: utf-8

"""
Exposes a run_tests() function that runs all tests in the project.

This module is for our test console script.

"""

import os
import sys
from unittest import TestProgram

from pystache.tests.common import PACKAGE_DIR, PROJECT_DIR, SPEC_TEST_DIR
from pystache.tests.doctesting import get_doctests
# TODO: change this to pystache.tests.spectesting.
from pystache.tests.test_mustachespec import get_spec_tests


UNITTEST_FILE_PREFIX = "test_"

# TODO: enhance this function to create spec-test tests.
def run_tests(sys_argv):
    """
    Run all tests in the project.

    Arguments:

      sys_argv: a reference to sys.argv.

    """
    try:
        # TODO: use optparse command options instead.
        project_dir = sys_argv[1]
        sys_argv.pop()
    except IndexError:
        project_dir = PROJECT_DIR

    if len(sys_argv) <= 1 or sys_argv[-1].startswith("-"):
        # Then no explicit module or test names were provided, so
        # auto-detect all unit tests.
        module_names = _discover_test_modules(PACKAGE_DIR)
        sys_argv.extend(module_names)

    _PystacheTestProgram._text_doctest_dir = project_dir
    _PystacheTestProgram._spec_test_dir = SPEC_TEST_DIR

    # We pass None for the module because we do not want the unittest
    # module to resolve module names relative to a given module.
    # (This would require importing all of the unittest modules from
    # this module.)  See the loadTestsFromName() method of the
    # unittest.TestLoader class for more details on this parameter.
    _PystacheTestProgram(argv=sys_argv, module=None)
    # No need to return since unitttest.main() exits.


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


# The function unittest.main() is an alias for unittest.TestProgram's
# constructor.  TestProgram's constructor calls self.runTests() as its
# final step, which expects self.test to be set.  The constructor sets
# the self.test attribute by calling one of self.testLoader's "loadTests"
# methods prior to callint self.runTests().  Each loadTest method returns
# a unittest.TestSuite instance.  Thus, self.test is set to a TestSuite
# instance prior to calling runTests().
class _PystacheTestProgram(TestProgram):

    """
    Instantiating an instance of this class runs all tests.

    """

    def runTests(self):
        # self.test is a unittest.TestSuite instance:
        #   http://docs.python.org/library/unittest.html#unittest.TestSuite
        tests = self.test

        doctest_suites = get_doctests(self._text_doctest_dir)
        tests.addTests(doctest_suites)

        spec_testcases = get_spec_tests(self._spec_test_dir)
        tests.addTests(spec_testcases)

        TestProgram.runTests(self)
