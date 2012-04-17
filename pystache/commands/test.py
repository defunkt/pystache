# coding: utf-8

"""
This module provides a command to test pystache (unit tests, doctests, etc).

"""

import sys

import pystache
from pystache.tests.main import Tester


def main(sys_argv=sys.argv):
    tester = Tester()
    tester.run_tests(package=pystache, sys_argv=sys_argv)


if __name__=='__main__':
    main()
