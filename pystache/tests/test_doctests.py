# coding: utf-8

"""
Creates unittest.TestSuite instances for the doctests in the project.

"""

# This module follows the guidance documented here:
#
#   http://docs.python.org/library/doctest.html#unittest-api
#

from pystache.tests.doctesting import get_module_doctests


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
# Normally, nosetests would interpret this function as a test case (because
# its name matches the test regular expression) and call it with zero arguments
# as opposed to the required three.  However, we are able to exclude it with
# an entry like the following in setup.cfg:
#
#   exclude=load_tests
#
# TODO: find a substitute for the load_tests protocol for Python versions
#   before version 2.7.
#
def load_tests(loader, tests, ignore):
    suites = get_module_doctests()
    tests.addTests(suites)

    return tests
