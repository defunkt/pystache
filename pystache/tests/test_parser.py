# coding: utf-8

"""
Unit tests of parser.py.

"""

import unittest

from pystache.parser import _compile_template_re as make_re


class RegularExpressionTestCase(unittest.TestCase):

    """Tests the regular expression returned by _compile_template_re()."""

    def test_re(self):
        """
        Test getting a key from a dictionary.

        """
        re = make_re()
        match = re.search("b  {{test}}")

        self.assertEqual(match.start(), 1)

