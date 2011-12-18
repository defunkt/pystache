# coding: utf-8

"""
Unit tests of template.py.

"""

import codecs
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

    def test_render__unicode(self):
        template = Template(u'foo')
        actual = template.render()
        self.assertTrue(isinstance(actual, unicode))
        self.assertEquals(actual, u'foo')

    def test_render__str(self):
        template = Template('foo')
        actual = template.render()
        self.assertTrue(isinstance(actual, str))
        self.assertEquals(actual, 'foo')

    def test_render__non_ascii_character(self):
        template = Template(u'Poincaré')
        actual = template.render()
        self.assertTrue(isinstance(actual, unicode))
        self.assertEquals(actual, u'Poincaré')

    def test_render__context(self):
        template = Template('Hi {{person}}', {'person': 'Mom'})
        self.assertEquals(template.render(), 'Hi Mom')

    def test_render__output_encoding(self):
        template = Template(u'Poincaré')
        actual = template.render('utf-8')
        self.assertTrue(isinstance(actual, str))
        self.assertEquals(actual, 'Poincaré')

