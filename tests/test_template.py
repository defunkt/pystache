# coding: utf-8

"""
Unit tests of template.py.

"""

import codecs
import unittest

from pystache.template import Template


class TemplateTestCase(unittest.TestCase):

    """Test the Template class."""

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
        """
        Test render(): passing a context.

        """
        template = Template('Hi {{person}}')
        self.assertEquals(template.render({'person': 'Mom'}), 'Hi Mom')

    def test_render__context_and_kwargs(self):
        """
        Test render(): passing a context and **kwargs.

        """
        template = Template('Hi {{person1}} and {{person2}}')
        self.assertEquals(template.render({'person1': 'Mom'}, person2='Dad'), 'Hi Mom and Dad')

    def test_render__kwargs_and_no_context(self):
        """
        Test render(): passing **kwargs and no context.

        """
        template = Template('Hi {{person}}')
        self.assertEquals(template.render(person='Mom'), 'Hi Mom')

    def test_render__context_and_kwargs__precedence(self):
        """
        Test render(): **kwargs takes precedence over context.

        """
        template = Template('Hi {{person}}')
        self.assertEquals(template.render({'person': 'Mom'}, person='Dad'), 'Hi Dad')

    def test_render__kwargs_does_not_modify_context(self):
        """
        Test render(): passing **kwargs does not modify the passed context.

        """
        context = {}
        template = Template('Hi {{person}}')
        template.render(context=context, foo="bar")
        self.assertEquals(context, {})

    def test_render__output_encoding(self):
        template = Template(u'Poincaré')
        template.output_encoding = 'utf-8'
        actual = template.render()
        self.assertTrue(isinstance(actual, str))
        self.assertEquals(actual, 'Poincaré')

    def test_render__tag_in_value(self):
        """
        Context values should not be treated as templates (issue #44).

        """
        template = Template('{{test}}')
        context = {'test': '{{hello}}'}
        actual = template.render(context)
        self.assertEquals(actual, '{{hello}}')

    def test_render__section_in_value(self):
        """
        Context values should not be treated as templates (issue #44).

        """
        template = Template('{{test}}')
        context = {'test': '{{#hello}}'}
        actual = template.render(context)
        self.assertEquals(actual, '{{#hello}}')
