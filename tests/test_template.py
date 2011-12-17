# coding: utf-8

"""
Unit tests of template.py.

"""

import unittest

from pystache.template import Template


class TemplateTestCase(unittest.TestCase):

    """Test the Template class."""

    def test_init__kwargs_with_no_context(self):
        """
        Test passing **kwargs with no context.

        """
        # This test checks that the following line raises no exception.
        template = Template(foo="bar")

    def test_init__kwargs_does_not_modify_context(self):
        """
        Test that passing **kwargs does not modify the passed context.

        """
        context = {}
        template = Template(context=context, foo="bar")
        self.assertEquals(context, {})

