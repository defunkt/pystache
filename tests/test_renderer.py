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

    def _renderer(self):
        return Renderer()

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
        renderer = Renderer()
        self.assertEquals(renderer.escape(">'"), "&gt;'")

    def test_init__escape__default_with_markupsafe(self):
        if not self._was_markupsafe_imported():
            # Then we cannot test this case.
            return
        self._restore_markupsafe()

        renderer = Renderer()
        self.assertEquals(renderer.escape(">'"), "&gt;&#39;")

    def test_init__escape(self):
        escape = lambda s: "foo" + s
        renderer = Renderer(escape=escape)
        self.assertEquals(renderer.escape("bar"), "foobar")

    def test_init__default_encoding__default(self):
        """
        Check the default value.

        """
        renderer = Renderer()
        self.assertEquals(renderer.default_encoding, sys.getdefaultencoding())

    def test_init__default_encoding(self):
        """
        Check that the constructor sets the attribute correctly.

        """
        renderer = Renderer(default_encoding="foo")
        self.assertEquals(renderer.default_encoding, "foo")

    def test_init__decode_errors__default(self):
        """
        Check the default value.

        """
        renderer = Renderer()
        self.assertEquals(renderer.decode_errors, 'strict')

    def test_init__decode_errors(self):
        """
        Check that the constructor sets the attribute correctly.

        """
        renderer = Renderer(decode_errors="foo")
        self.assertEquals(renderer.decode_errors, "foo")

    def test_unicode(self):
        renderer = Renderer()
        actual = renderer.literal("abc")
        self.assertEquals(actual, "abc")
        self.assertEquals(type(actual), unicode)

    def test_unicode__default_encoding(self):
        renderer = Renderer()
        s = "é"

        renderer.default_encoding = "ascii"
        self.assertRaises(UnicodeDecodeError, renderer.unicode, s)

        renderer.default_encoding = "utf-8"
        self.assertEquals(renderer.unicode(s), u"é")

    def test_unicode__decode_errors(self):
        renderer = Renderer()
        s = "é"

        renderer.default_encoding = "ascii"
        renderer.decode_errors = "strict"
        self.assertRaises(UnicodeDecodeError, renderer.unicode, s)

        renderer.decode_errors = "replace"
        # U+FFFD is the official Unicode replacement character.
        self.assertEquals(renderer.unicode(s), u'\ufffd\ufffd')

    def test_literal__with_markupsafe(self):
        if not self._was_markupsafe_imported():
            # Then we cannot test this case.
            return
        self._restore_markupsafe()

        _renderer = Renderer()
        _renderer.default_encoding = "utf_8"

        # Check the standard case.
        actual = _renderer.literal("abc")
        self.assertEquals(actual, "abc")
        self.assertEquals(type(actual), renderer.markupsafe.Markup)

        s = "é"
        # Check that markupsafe respects default_encoding.
        self.assertEquals(_renderer.literal(s), u"é")
        _renderer.default_encoding = "ascii"
        self.assertRaises(UnicodeDecodeError, _renderer.literal, s)

        # Check that markupsafe respects decode_errors.
        _renderer.decode_errors = "replace"
        self.assertEquals(_renderer.literal(s), u'\ufffd\ufffd')

    def test_render__unicode(self):
        renderer = Renderer()
        actual = renderer.render(u'foo')
        self.assertTrue(isinstance(actual, unicode))
        self.assertEquals(actual, u'foo')

    def test_render__str(self):
        renderer = Renderer()
        actual = renderer.render('foo')
        self.assertTrue(isinstance(actual, unicode))
        self.assertEquals(actual, 'foo')

    def test_render__non_ascii_character(self):
        renderer = Renderer()
        actual = renderer.render(u'Poincaré')
        self.assertTrue(isinstance(actual, unicode))
        self.assertEquals(actual, u'Poincaré')

    def test_render__context(self):
        """
        Test render(): passing a context.

        """
        renderer = Renderer()
        self.assertEquals(renderer.render('Hi {{person}}', {'person': 'Mom'}), 'Hi Mom')

    def test_render__context_and_kwargs(self):
        """
        Test render(): passing a context and **kwargs.

        """
        renderer = Renderer()
        template = 'Hi {{person1}} and {{person2}}'
        self.assertEquals(renderer.render(template, {'person1': 'Mom'}, person2='Dad'), 'Hi Mom and Dad')

    def test_render__kwargs_and_no_context(self):
        """
        Test render(): passing **kwargs and no context.

        """
        renderer = Renderer()
        self.assertEquals(renderer.render('Hi {{person}}', person='Mom'), 'Hi Mom')

    def test_render__context_and_kwargs__precedence(self):
        """
        Test render(): **kwargs takes precedence over context.

        """
        renderer = Renderer()
        self.assertEquals(renderer.render('Hi {{person}}', {'person': 'Mom'}, person='Dad'), 'Hi Dad')

    def test_render__kwargs_does_not_modify_context(self):
        """
        Test render(): passing **kwargs does not modify the passed context.

        """
        context = {}
        renderer = Renderer()
        renderer.render('Hi {{person}}', context=context, foo="bar")
        self.assertEquals(context, {})

    def test_render__output_encoding(self):
        renderer = Renderer()
        renderer.output_encoding = 'utf-8'
        actual = renderer.render(u'Poincaré')
        self.assertTrue(isinstance(actual, str))
        self.assertEquals(actual, 'Poincaré')

    def test_render__nonascii_template(self):
        """
        Test passing a non-unicode template with non-ascii characters.

        """
        renderer = Renderer(output_encoding="utf-8")
        template = "déf"

        # Check that decode_errors and default_encoding are both respected.
        renderer.decode_errors = 'ignore'
        renderer.default_encoding = 'ascii'
        self.assertEquals(renderer.render(template), "df")

        renderer.default_encoding = 'utf_8'
        self.assertEquals(renderer.render(template), "déf")

    # By testing that Renderer.render() constructs the RenderEngine instance
    # correctly, we no longer need to test the rendering code paths through
    # the Renderer.  We can test rendering paths through only the RenderEngine
    # for the same amount of code coverage.
    def test_make_render_engine__load_template(self):
        """
        Test that _make_render_engine() passes the right load_template.

        """
        renderer = Renderer()
        renderer.load_template = "foo"  # in real life, this would be a function.

        engine = renderer._make_render_engine()
        self.assertEquals(engine.load_template, "foo")

    def test_make_render_engine__literal(self):
        """
        Test that _make_render_engine() passes the right literal.

        """
        renderer = Renderer()
        renderer.literal = "foo"  # in real life, this would be a function.

        engine = renderer._make_render_engine()
        self.assertEquals(engine.literal, "foo")

    def test_make_render_engine__escape(self):
        """
        Test that _make_render_engine() passes the right escape.

        """
        renderer = Renderer()
        renderer.unicode = lambda s: s.upper()  # a test version.
        renderer.escape = lambda s: "**" + s  # a test version.

        engine = renderer._make_render_engine()
        escape = engine.escape

        self.assertEquals(escape(u"foo"), "**foo")

        # Test that escape converts str strings to unicode first.
        self.assertEquals(escape("foo"), "**FOO")
