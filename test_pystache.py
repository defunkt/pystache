#!/usr/bin/env python
# coding: utf-8

"""
Runs project tests.

This script is a substitute for running--

    python -m pystache.commands.test

It is useful in Python 2.4 because the -m flag does not accept subpackages
in Python 2.4:

  http://docs.python.org/using/cmdline.html#cmdoption-m

"""

from pystache.commands.test import main

if __name__=='__main__':
    main()
