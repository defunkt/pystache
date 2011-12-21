# coding: utf-8

"""
Unit tests of template.py.

"""

import codecs
import unittest

from pystache import template
from pystache.template import Template


class TemplateTestCase(unittest.TestCase):

    """Test the Template class."""

    def setUp(self):
        """
        Disable markupsafe.

        """
        self.original_markupsafe = template.markupsafe
        template.markupsafe = None

    def tearDown(self):
        self._restore_markupsafe()

    def _was_markupsafe_imported(self):
        return bool(self.original_markupsafe)

    def _restore_markupsafe(self):
        """
        Restore markupsafe to its original state.

        """
        template.markupsafe = self.original_markupsafe

    def test_init__escape__default_without_markupsafe(self):
        template = Template()
        self.assertEquals(template.escape(">'"), "&gt;'")

    def test_init__escape__default_with_markupsafe(self):
        if not self._was_markupsafe_imported():
            # Then we cannot test this case.
            return
        self._restore_markupsafe()

        template = Template()
        self.assertEquals(template.escape(">'"), "&gt;&#39;")

    def test_init__escape(self):
        escape = lambda s: "foo" + s
        template = Template(escape=escape)
        self.assertEquals(template.escape("bar"), "foobar")

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

    def test_render__section__lambda(self):
        template = Template('{{#test}}Mom{{/test}}')
        context = {'test': (lambda text: 'Hi %s' % text)}
        actual = template.render(context)
        self.assertEquals(actual, 'Hi Mom')

    def test_render__section__lambda__tag_in_output(self):
        """
        Check that callable output isn't treated as a template string (issue #46).

        """
        template = Template('{{#test}}Mom{{/test}}')
        context = {'test': (lambda text: '{{hi}} %s' % text)}
        actual = template.render(context)
        self.assertEquals(actual, '{{hi}} Mom')

    def test_render__html_escape(self):
        context = {'test': '1 < 2'}
        template = Template('{{test}}')

        self.assertEquals(template.render(context), '1 &lt; 2')

    def test_render__html_escape_disabled(self):
        context = {'test': '1 < 2'}
        template = Template('{{test}}')

        self.assertEquals(template.render(context), '1 &lt; 2')

        template.escape = lambda s: s
        self.assertEquals(template.render(context), '1 < 2')

    def test_render__html_escape_disabled_with_partial(self):
        context = {'test': '1 < 2'}
        load_template = lambda name: '{{test}}'
        template = Template('{{>partial}}', load_template=load_template)

        self.assertEquals(template.render(context), '1 &lt; 2')

        template.escape = lambda s: s
        self.assertEquals(template.render(context), '1 < 2')

    def test_render__html_escape_disabled_with_non_false_value(self):
        context = {'section': {'test': '1 < 2'}}
        template = Template('{{#section}}{{test}}{{/section}}')

        self.assertEquals(template.render(context), '1 &lt; 2')

        template.escape = lambda s: s
        self.assertEquals(template.render(context), '1 < 2')

    def test_render__list_referencing_outer_context(self):
        """
        Check that list items can access the parent context.

        For sections whose value is a list, check that items in the list
        have access to the values inherited from the parent context
        when rendering.

        """
        context = {
            "list": [{"name": "Al"}, {"name": "Bo"}],
            "greeting": "Hi",
        }
        template = Template("{{#list}}{{name}}: {{greeting}}; {{/list}}")

        self.assertEquals(template.render(context), "Al: Hi; Bo: Hi; ")
