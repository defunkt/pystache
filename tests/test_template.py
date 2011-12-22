# coding: utf-8

"""
Unit tests of template.py.

"""

import codecs
import sys
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

    def test__was_markupsafe_imported(self):
        """
        Test that our helper function works.

        """
        markupsafe = None
        try:
            import markupsafe
        except:
            pass

        self.assertEquals(bool(markupsafe), self._was_markupsafe_imported())

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

    def test_init__default_encoding__default(self):
        """
        Check the default value.

        """
        template = Template()
        self.assertEquals(template.default_encoding, sys.getdefaultencoding())

    def test_init__default_encoding(self):
        """
        Check that the constructor sets the attribute correctly.

        """
        template = Template(default_encoding="foo")
        self.assertEquals(template.default_encoding, "foo")

    def test_init__decode_errors__default(self):
        """
        Check the default value.

        """
        template = Template()
        self.assertEquals(template.decode_errors, 'strict')

    def test_init__decode_errors(self):
        """
        Check that the constructor sets the attribute correctly.

        """
        template = Template(decode_errors="foo")
        self.assertEquals(template.decode_errors, "foo")

    def test_unicode(self):
        template = Template()
        actual = template.literal("abc")
        self.assertEquals(actual, "abc")
        self.assertEquals(type(actual), unicode)

    def test_unicode__default_encoding(self):
        template = Template()
        s = "é"

        template.default_encoding = "ascii"
        self.assertRaises(UnicodeDecodeError, template.unicode, s)

        template.default_encoding = "utf-8"
        self.assertEquals(template.unicode(s), u"é")

    def test_unicode__decode_errors(self):
        template = Template()
        s = "é"

        template.default_encoding = "ascii"
        template.decode_errors = "strict"
        self.assertRaises(UnicodeDecodeError, template.unicode, s)

        template.decode_errors = "replace"
        # U+FFFD is the official Unicode replacement character.
        self.assertEquals(template.unicode(s), u'\ufffd\ufffd')

    def test_literal__with_markupsafe(self):
        if not self._was_markupsafe_imported():
            # Then we cannot test this case.
            return
        self._restore_markupsafe()

        _template = Template()
        _template.default_encoding = "utf_8"

        # Check the standard case.
        actual = _template.literal("abc")
        self.assertEquals(actual, "abc")
        self.assertEquals(type(actual), template.markupsafe.Markup)

        s = "é"
        # Check that markupsafe respects default_encoding.
        self.assertEquals(_template.literal(s), u"é")
        _template.default_encoding = "ascii"
        self.assertRaises(UnicodeDecodeError, _template.literal, s)

        # Check that markupsafe respects decode_errors.
        _template.decode_errors = "replace"
        self.assertEquals(_template.literal(s), u'\ufffd\ufffd')

    def test_render__unicode(self):
        template = Template(u'foo')
        actual = template.render()
        self.assertTrue(isinstance(actual, unicode))
        self.assertEquals(actual, u'foo')

    def test_render__str(self):
        template = Template('foo')
        actual = template.render()
        self.assertTrue(isinstance(actual, unicode))
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

    def test_render__encoding_in_context_value(self):
        template = Template('{{test}}')
        context = {'test': "déf"}

        template.decode_errors = 'ignore'
        template.default_encoding = 'ascii'
        self.assertEquals(template.render(context), "df")

        template.default_encoding = 'utf_8'
        self.assertEquals(template.render(context), u"déf")

    def test_render__encoding_in_section_context_value(self):
        template = Template('{{#test}}{{foo}}{{/test}}')
        context = {'test': {'foo': "déf"}}

        template.decode_errors = 'ignore'
        template.default_encoding = 'ascii'
        self.assertEquals(template.render(context), "df")

        template.default_encoding = 'utf_8'
        self.assertEquals(template.render(context), u"déf")

    def test_render__encoding_in_partial_context_value(self):
        load_template = lambda x: "{{foo}}"
        template = Template('{{>partial}}', load_template=load_template)
        context = {'foo': "déf"}

        template.decode_errors = 'ignore'
        template.default_encoding = 'ascii'
        self.assertEquals(template.render(context), "df")

        template.default_encoding = 'utf_8'
        self.assertEquals(template.render(context), u"déf")

    def test_render__nonascii_template(self):
        """
        Test passing a non-unicode template with non-ascii characters.

        """
        template = Template("déf", output_encoding="utf-8")

        # Check that decode_errors and default_encoding are both respected.
        template.decode_errors = 'ignore'
        template.default_encoding = 'ascii'
        self.assertEquals(template.render(), "df")

        template.default_encoding = 'utf_8'
        self.assertEquals(template.render(), "déf")
