# coding: utf-8

"""
Unit tests of template.py.

"""

import unittest

from pystache.template import Template


class TemplateTestCase(unittest.TestCase):

    def test_init__kwargs_with_no_context(self):
        """
        Test passing **kwargs with no context.

        """
        # This test checks that the following line raises no exception.
        template = Template(foo="bar")

