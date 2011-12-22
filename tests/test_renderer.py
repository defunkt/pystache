# coding: utf-8

"""
Unit tests of template.py.

"""

import codecs
import sys
import unittest

from pystache import renderer
from pystache.renderer import Renderer


class RendererTestCase(unittest.TestCase):

    """Test the Renderer class."""

    def setUp(self):
        """
        Disable markupsafe.

        """
        self.original_markupsafe = renderer.markupsafe
        renderer.markupsafe = None

    def tearDown(self):
        self._restore_markupsafe()

    def _was_markupsafe_imported(self):
        return bool(self.original_markupsafe)

    def _restore_markupsafe(self):
        """
        Restore markupsafe to its original state.

        """
        renderer.markupsafe = self.original_markupsafe

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
        template = Renderer()
        self.assertEquals(template.escape(">'"), "&gt;'")

    def test_init__escape__default_with_markupsafe(self):
        if not self._was_markupsafe_imported():
            # Then we cannot test this case.
            return
        self._restore_markupsafe()

        template = Renderer()
        self.assertEquals(template.escape(">'"), "&gt;&#39;")

    def test_init__escape(self):
        escape = lambda s: "foo" + s
        template = Renderer(escape=escape)
        self.assertEquals(template.escape("bar"), "foobar")

    def test_init__default_encoding__default(self):
        """
        Check the default value.

        """
        template = Renderer()
        self.assertEquals(template.default_encoding, sys.getdefaultencoding())

    def test_init__default_encoding(self):
        """
        Check that the constructor sets the attribute correctly.

        """
        template = Renderer(default_encoding="foo")
        self.assertEquals(template.default_encoding, "foo")

    def test_init__decode_errors__default(self):
        """
        Check the default value.

        """
        template = Renderer()
        self.assertEquals(template.decode_errors, 'strict')

    def test_init__decode_errors(self):
        """
        Check that the constructor sets the attribute correctly.

        """
        template = Renderer(decode_errors="foo")
        self.assertEquals(template.decode_errors, "foo")

    def test_unicode(self):
        template = Renderer()
        actual = template.literal("abc")
        self.assertEquals(actual, "abc")
        self.assertEquals(type(actual), unicode)

    def test_unicode__default_encoding(self):
        template = Renderer()
        s = "é"

        template.default_encoding = "ascii"
        self.assertRaises(UnicodeDecodeError, template.unicode, s)

        template.default_encoding = "utf-8"
        self.assertEquals(template.unicode(s), u"é")

    def test_unicode__decode_errors(self):
        template = Renderer()
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

        template = Renderer()
        template.default_encoding = "utf_8"

        # Check the standard case.
        actual = template.literal("abc")
        self.assertEquals(actual, "abc")
        self.assertEquals(type(actual), renderer.markupsafe.Markup)

        s = "é"
        # Check that markupsafe respects default_encoding.
        self.assertEquals(template.literal(s), u"é")
        template.default_encoding = "ascii"
        self.assertRaises(UnicodeDecodeError, template.literal, s)

        # Check that markupsafe respects decode_errors.
        template.decode_errors = "replace"
        self.assertEquals(template.literal(s), u'\ufffd\ufffd')

    def test_render__unicode(self):
        template = Renderer(u'foo')
        actual = template.render()
        self.assertTrue(isinstance(actual, unicode))
        self.assertEquals(actual, u'foo')

    def test_render__str(self):
        template = Renderer('foo')
        actual = template.render()
        self.assertTrue(isinstance(actual, unicode))
        self.assertEquals(actual, 'foo')

    def test_render__non_ascii_character(self):
        template = Renderer(u'Poincaré')
        actual = template.render()
        self.assertTrue(isinstance(actual, unicode))
        self.assertEquals(actual, u'Poincaré')

    def test_render__context(self):
        """
        Test render(): passing a context.

        """
        template = Renderer('Hi {{person}}')
        self.assertEquals(template.render({'person': 'Mom'}), 'Hi Mom')

    def test_render__context_and_kwargs(self):
        """
        Test render(): passing a context and **kwargs.

        """
        template = Renderer('Hi {{person1}} and {{person2}}')
        self.assertEquals(template.render({'person1': 'Mom'}, person2='Dad'), 'Hi Mom and Dad')

    def test_render__kwargs_and_no_context(self):
        """
        Test render(): passing **kwargs and no context.

        """
        template = Renderer('Hi {{person}}')
        self.assertEquals(template.render(person='Mom'), 'Hi Mom')

    def test_render__context_and_kwargs__precedence(self):
        """
        Test render(): **kwargs takes precedence over context.

        """
        template = Renderer('Hi {{person}}')
        self.assertEquals(template.render({'person': 'Mom'}, person='Dad'), 'Hi Dad')

    def test_render__kwargs_does_not_modify_context(self):
        """
        Test render(): passing **kwargs does not modify the passed context.

        """
        context = {}
        template = Renderer('Hi {{person}}')
        template.render(context=context, foo="bar")
        self.assertEquals(context, {})

    def test_render__output_encoding(self):
        template = Renderer(u'Poincaré')
        template.output_encoding = 'utf-8'
        actual = template.render()
        self.assertTrue(isinstance(actual, str))
        self.assertEquals(actual, 'Poincaré')

    def test_render__nonascii_template(self):
        """
        Test passing a non-unicode template with non-ascii characters.

        """
        template = Renderer("déf", output_encoding="utf-8")

        # Check that decode_errors and default_encoding are both respected.
        template.decode_errors = 'ignore'
        template.default_encoding = 'ascii'
        self.assertEquals(template.render(), "df")

        template.default_encoding = 'utf_8'
        self.assertEquals(template.render(), "déf")

    # By testing that Renderer.render() constructs the RenderEngine instance
    # correctly, we no longer need to test the rendering code paths through
    # the Renderer.  We can test rendering paths through only the RenderEngine
    # for the same amount of code coverage.
    def test_make_render_engine__load_template(self):
        """
        Test that _make_render_engine() passes the right load_template.

        """
        template = Renderer()
        template.load_template = "foo"  # in real life, this would be a function.

        engine = template._make_render_engine()
        self.assertEquals(engine.load_template, "foo")

    def test_make_render_engine__literal(self):
        """
        Test that _make_render_engine() passes the right literal.

        """
        template = Renderer()
        template.literal = "foo"  # in real life, this would be a function.

        engine = template._make_render_engine()
        self.assertEquals(engine.literal, "foo")

    def test_make_render_engine__escape(self):
        """
        Test that _make_render_engine() passes the right escape.

        """
        template = Renderer()
        template.unicode = lambda s: s.upper()  # a test version.
        template.escape = lambda s: "**" + s  # a test version.

        engine = template._make_render_engine()
        escape = engine.escape

        self.assertEquals(escape(u"foo"), "**foo")

        # Test that escape converts str strings to unicode first.
        self.assertEquals(escape("foo"), "**FOO")
