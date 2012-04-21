# coding: utf-8

"""
This module provides a command to test pystache (unit tests, doctests, etc).

"""

import sys

from pystache.tests.main import TestHarness


def main(sys_argv=sys.argv):
    harness = TestHarness()
    harness.run_tests(sys_argv=sys_argv)


if __name__=='__main__':
    main()
