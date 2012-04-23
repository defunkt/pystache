# coding: utf-8

"""
Exposes a run_tests() function that runs all tests in the project.

This module is for our test console script.

"""

import os
import sys
from unittest import TestProgram

from pystache.tests.common import PACKAGE_DIR, PROJECT_DIR, SPEC_TEST_DIR, UNITTEST_FILE_PREFIX
from pystache.tests.common import get_module_names
from pystache.tests.doctesting import get_doctests
from pystache.tests.spectesting import get_spec_tests


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
        sys_argv.pop(1)
    except IndexError:
        project_dir = PROJECT_DIR

    try:
        # TODO: use optparse command options instead.
        spec_test_dir = sys_argv[1]
        sys_argv.pop(1)
    except IndexError:
        spec_test_dir = SPEC_TEST_DIR

    if len(sys_argv) <= 1 or sys_argv[-1].startswith("-"):
        # Then no explicit module or test names were provided, so
        # auto-detect all unit tests.
        module_names = _discover_test_modules(PACKAGE_DIR)
        sys_argv.extend(module_names)

    _PystacheTestProgram._text_doctest_dir = project_dir
    _PystacheTestProgram._spec_test_dir = spec_test_dir

    # We pass None for the module because we do not want the unittest
    # module to resolve module names relative to a given module.
    # (This would require importing all of the unittest modules from
    # this module.)  See the loadTestsFromName() method of the
    # unittest.TestLoader class for more details on this parameter.
    _PystacheTestProgram(argv=sys_argv, module=None)
    # No need to return since unitttest.main() exits.


def _discover_test_modules(package_dir):
    """
    Discover and return a sorted list of the names of unit-test modules.

    """
    def is_unittest_module(path):
        file_name = os.path.basename(path)
        return file_name.startswith(UNITTEST_FILE_PREFIX)

    names = get_module_names(package_dir=package_dir, should_include=is_unittest_module)

    # This is a sanity check to ensure that the unit-test discovery
    # methods are working.
    if len(names) < 1:
        raise Exception("No unit-test modules found--\n  in %s" % package_dir)

    return names


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
