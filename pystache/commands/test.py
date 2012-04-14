# coding: utf-8

"""
This module provides a command to test pystache (unit tests, doctests, etc).

"""

import sys

# TODO: make nose unnecessary.
import nose

import pystache


def main(sys_argv):
    # This does not work with the --with-doctest flag yet because of the
    # following issue:
    #   https://github.com/nose-devs/nose/issues/383
    nose.main(module=pystache)


if __name__=='__main__':
    main(sys.argv)
