# coding: utf-8

"""
Unit tests of template.py.

"""

import codecs
import sys
import unittest

from pystache import renderer
from pystache.renderer import Renderer
from pystache.loader import Loader

class RendererInitTestCase(unittest.TestCase):

    """A class to test the Renderer.__init__() method."""

    def test_loader(self):
        """Test that the loader attribute is set correctly."""
        loader = {'foo': 'bar'}
        r = Renderer(loader=loader)
        self.assertEquals(r.loader, {'foo': 'bar'})

    def test_loader__default(self):
        """Test that the default loader is constructed correctly."""
        r = Renderer()
        actual = r.loader

        expected = Loader()

        self.assertEquals(type(actual), type(expected))
        self.assertEquals(actual.__dict__, expected.__dict__)

    def test_loader__default__default_encoding(self):
        """Test that the default loader inherits the default_encoding."""
        r = Renderer(default_encoding='foo')
        actual = r.loader

        expected = Loader(encoding='foo')
        self.assertEquals(actual.template_encoding, expected.template_encoding)
        # Check all attributes for good measure.
        self.assertEquals(actual.__dict__, expected.__dict__)

    def test_loader__default__decode_errors(self):
        """Test that the default loader inherits the decode_errors."""
        r = Renderer(decode_errors='foo')
        actual = r.loader

        expected = Loader(decode_errors='foo')
        self.assertEquals(actual.decode_errors, expected.decode_errors)
        # Check all attributes for good measure.
        self.assertEquals(actual.__dict__, expected.__dict__)



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

    def test_make_load_partial(self):
        """
        Test the _make_load_partial() method.

        """
        partials = {'foo': 'bar'}
        renderer = Renderer(loader=partials)
        load_partial = renderer._make_load_partial()

        actual = load_partial('foo')
        self.assertEquals(actual, 'bar')
        self.assertEquals(type(actual), unicode, "RenderEngine requires that "
            "load_partial return unicode strings.")

    def test_make_load_partial__unicode(self):
        """
        Test _make_load_partial(): that load_partial doesn't "double-decode" Unicode.

        """
        renderer = Renderer()

        renderer.loader = {'partial': 'foo'}
        load_partial = renderer._make_load_partial()
        self.assertEquals(load_partial("partial"), "foo")

        # Now with a value that is already unicode.
        renderer.loader = {'partial': u'foo'}
        load_partial = renderer._make_load_partial()
        # If the next line failed, we would get the following error:
        #   TypeError: decoding Unicode is not supported
        self.assertEquals(load_partial("partial"), "foo")

    # By testing that Renderer.render() constructs the RenderEngine instance
    # correctly, we no longer need to test the rendering code paths through
    # the Renderer.  We can test rendering paths through only the RenderEngine
    # for the same amount of code coverage.
    def test_make_render_engine__load_partial(self):
        """
        Test that _make_render_engine() constructs and passes load_partial correctly.

        """
        partials = {'partial': 'foo'}
        renderer = Renderer(loader=partials)
        renderer.unicode = lambda s: s.upper()  # a test version.

        engine = renderer._make_render_engine()
        # Make sure it calls unicode.
        self.assertEquals(engine.load_partial('partial'), "FOO")

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
