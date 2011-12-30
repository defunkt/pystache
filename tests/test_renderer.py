# coding: utf-8

"""
Unit tests of template.py.

"""

import codecs
import os
import sys
import unittest

from examples.simple import Simple
from pystache import renderer
from pystache.renderer import Renderer
from pystache.locator import Locator

from .common import get_data_path
from .data.templates import SayHello


class RendererInitTestCase(unittest.TestCase):

    """
    Tests the Renderer.__init__() method.

    """

    def test_partials__default(self):
        """
        Test the default value.

        """
        renderer = Renderer()
        self.assertTrue(renderer.partials is None)

    def test_partials(self):
        """
        Test that the attribute is set correctly.

        """
        renderer = Renderer(partials={'foo': 'bar'})
        self.assertEquals(renderer.partials, {'foo': 'bar'})

    def test_escape__default(self):
        escape = Renderer().escape

        self.assertEquals(escape(">"), "&gt;")
        self.assertEquals(escape('"'), "&quot;")
        # Single quotes are not escaped.
        self.assertEquals(escape("'"), "'")

    def test_escape(self):
        escape = lambda s: "**" + s
        renderer = Renderer(escape=escape)
        self.assertEquals(renderer.escape("bar"), "**bar")

    def test_default_encoding__default(self):
        """
        Check the default value.

        """
        renderer = Renderer()
        self.assertEquals(renderer.default_encoding, sys.getdefaultencoding())

    def test_default_encoding(self):
        """
        Check that the constructor sets the attribute correctly.

        """
        renderer = Renderer(default_encoding="foo")
        self.assertEquals(renderer.default_encoding, "foo")

    def test_decode_errors__default(self):
        """
        Check the default value.

        """
        renderer = Renderer()
        self.assertEquals(renderer.decode_errors, 'strict')

    def test_decode_errors(self):
        """
        Check that the constructor sets the attribute correctly.

        """
        renderer = Renderer(decode_errors="foo")
        self.assertEquals(renderer.decode_errors, "foo")

    def test_file_encoding__default(self):
        """
        Check the file_encoding default.

        """
        renderer = Renderer()
        self.assertEquals(renderer.file_encoding, renderer.default_encoding)

    def test_file_encoding(self):
        """
        Check that the file_encoding attribute is set correctly.

        """
        renderer = Renderer(file_encoding='foo')
        self.assertEquals(renderer.file_encoding, 'foo')

    def test_file_extension__default(self):
        """
        Check the file_extension default.

        """
        renderer = Renderer()
        self.assertEquals(renderer.file_extension, 'mustache')

    def test_file_extension(self):
        """
        Check that the file_encoding attribute is set correctly.

        """
        renderer = Renderer(file_extension='foo')
        self.assertEquals(renderer.file_extension, 'foo')

    def test_search_dirs__default(self):
        """
        Check the search_dirs default.

        """
        renderer = Renderer()
        self.assertEquals(renderer.search_dirs, [os.curdir])

    def test_search_dirs__string(self):
        """
        Check that the search_dirs attribute is set correctly when a string.

        """
        renderer = Renderer(search_dirs='foo')
        self.assertEquals(renderer.search_dirs, ['foo'])

    def test_search_dirs__list(self):
        """
        Check that the search_dirs attribute is set correctly when a list.

        """
        renderer = Renderer(search_dirs=['foo'])
        self.assertEquals(renderer.search_dirs, ['foo'])


class RendererTestCase(unittest.TestCase):

    """Test the Renderer class."""

    def _renderer(self):
        return Renderer()

    ## Test Renderer.unicode().

    def test_unicode__default_encoding(self):
        """
        Test that the default_encoding attribute is respected.

        """
        renderer = Renderer()
        s = "é"

        renderer.default_encoding = "ascii"
        self.assertRaises(UnicodeDecodeError, renderer.unicode, s)

        renderer.default_encoding = "utf-8"
        self.assertEquals(renderer.unicode(s), u"é")

    def test_unicode__decode_errors(self):
        """
        Test that the decode_errors attribute is respected.

        """
        renderer = Renderer()
        renderer.default_encoding = "ascii"
        s = "déf"

        renderer.decode_errors = "ignore"
        self.assertEquals(renderer.unicode(s), "df")

        renderer.decode_errors = "replace"
        # U+FFFD is the official Unicode replacement character.
        self.assertEquals(renderer.unicode(s), u'd\ufffd\ufffdf')

    ## Test the read() method.

    def _read(self, renderer, filename):
        path = get_data_path(filename)
        return renderer.read(path)

    def test_read(self):
        renderer = Renderer()
        actual = self._read(renderer, 'ascii.mustache')
        self.assertEquals(actual, 'ascii: abc')

    def test_read__returns_unicode(self):
        renderer = Renderer()
        actual = self._read(renderer, 'ascii.mustache')
        self.assertEquals(type(actual), unicode)

    def test_read__file_encoding(self):
        filename = 'nonascii.mustache'

        renderer = Renderer()
        renderer.file_encoding = 'ascii'

        self.assertRaises(UnicodeDecodeError, self._read, renderer, filename)
        renderer.file_encoding = 'utf-8'
        actual = self._read(renderer, filename)
        self.assertEquals(actual, u'non-ascii: é')

    def test_read__decode_errors(self):
        filename = 'nonascii.mustache'
        renderer = Renderer()

        self.assertRaises(UnicodeDecodeError, self._read, renderer, filename)
        renderer.decode_errors = 'ignore'
        actual = self._read(renderer, filename)
        self.assertEquals(actual, 'non-ascii: ')

    ## Test the make_locator() method.

    def test_make_locator__return_type(self):
        """
        Test that make_locator() returns a Locator.

        """
        renderer = Renderer()
        locator = renderer.make_locator()

        self.assertEquals(type(locator), Locator)

    def test_make_locator__file_extension(self):
        """
        Test that make_locator() respects the file_extension attribute.

        """
        renderer = Renderer()
        renderer.file_extension = 'foo'

        locator = renderer.make_locator()

        self.assertEquals(locator.template_extension, 'foo')

    # This test is a sanity check.  Strictly speaking, it shouldn't
    # be necessary based on our tests above.
    def test_make_locator__default(self):
        renderer = Renderer()
        actual = renderer.make_locator()

        expected = Locator()

        self.assertEquals(type(actual), type(expected))
        self.assertEquals(actual.template_extension, expected.template_extension)

    ## Test the render() method.

    def test_render__return_type(self):
        """
        Check that render() returns a string of type unicode.

        """
        renderer = Renderer()
        rendered = renderer.render('foo')
        self.assertEquals(type(rendered), unicode)

    def test_render__unicode(self):
        renderer = Renderer()
        actual = renderer.render(u'foo')
        self.assertEquals(actual, u'foo')

    def test_render__str(self):
        renderer = Renderer()
        actual = renderer.render('foo')
        self.assertEquals(actual, 'foo')

    def test_render__non_ascii_character(self):
        renderer = Renderer()
        actual = renderer.render(u'Poincaré')
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

    def test_render__nonascii_template(self):
        """
        Test passing a non-unicode template with non-ascii characters.

        """
        renderer = Renderer()
        template = "déf"

        # Check that decode_errors and default_encoding are both respected.
        renderer.decode_errors = 'ignore'
        renderer.default_encoding = 'ascii'
        self.assertEquals(renderer.render(template), "df")

        renderer.default_encoding = 'utf_8'
        self.assertEquals(renderer.render(template), u"déf")

    def test_make_load_partial(self):
        """
        Test the _make_load_partial() method.

        """
        renderer = Renderer()
        renderer.partials = {'foo': 'bar'}
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

        renderer.partials = {'partial': 'foo'}
        load_partial = renderer._make_load_partial()
        self.assertEquals(load_partial("partial"), "foo")

        # Now with a value that is already unicode.
        renderer.partials = {'partial': u'foo'}
        load_partial = renderer._make_load_partial()
        # If the next line failed, we would get the following error:
        #   TypeError: decoding Unicode is not supported
        self.assertEquals(load_partial("partial"), "foo")

    def test_render_path(self):
        """
        Test the render_path() method.

        """
        renderer = Renderer()
        path = get_data_path('say_hello.mustache')
        actual = renderer.render_path(path, to='foo')
        self.assertEquals(actual, "Hello, foo")

    def test_render__object(self):
        """
        Test rendering an object instance.

        """
        renderer = Renderer()

        say_hello = SayHello()
        actual = renderer.render(say_hello)
        self.assertEquals('Hello, World', actual)

        actual = renderer.render(say_hello, to='Mars')
        self.assertEquals('Hello, Mars', actual)

    def test_render__view(self):
        """
        Test rendering a View instance.

        """
        renderer = Renderer()

        view = Simple()
        actual = renderer.render(view)
        self.assertEquals('Hi pizza!', actual)


# By testing that Renderer.render() constructs the right RenderEngine,
# we no longer need to exercise all rendering code paths through
# the Renderer.  It suffices to test rendering paths through the
# RenderEngine for the same amount of code coverage.
class Renderer_MakeRenderEngineTests(unittest.TestCase):

    """
    Check the RenderEngine returned by Renderer._make_render_engine().

    """

    ## Test the engine's load_partial attribute.

    def test__load_partial__returns_unicode(self):
        """
        Check that load_partial returns unicode (and not a subclass).

        """
        class MyUnicode(unicode):
            pass

        renderer = Renderer()
        renderer.default_encoding = 'ascii'
        renderer.partials = {'str': 'foo', 'subclass': MyUnicode('abc')}

        engine = renderer._make_render_engine()

        actual = engine.load_partial('str')
        self.assertEquals(actual, "foo")
        self.assertEquals(type(actual), unicode)

        # Check that unicode subclasses are not preserved.
        actual = engine.load_partial('subclass')
        self.assertEquals(actual, "abc")
        self.assertEquals(type(actual), unicode)

    def test__load_partial__not_found(self):
        """
        Check that load_partial provides a nice message when a template is not found.

        """
        renderer = Renderer()
        renderer.partials = {}

        engine = renderer._make_render_engine()
        load_partial = engine.load_partial

        try:
            load_partial("foo")
            raise Exception("Shouldn't get here")
        except Exception, err:
            self.assertEquals(str(err), "Partial not found with name: 'foo'")

    ## Test the engine's literal attribute.

    def test__literal__uses_renderer_unicode(self):
        """
        Test that literal uses the renderer's unicode function.

        """
        renderer = Renderer()
        renderer.unicode = lambda s: s.upper()

        engine = renderer._make_render_engine()
        literal = engine.literal

        self.assertEquals(literal("foo"), "FOO")

    def test__literal__handles_unicode(self):
        """
        Test that literal doesn't try to "double decode" unicode.

        """
        renderer = Renderer()
        renderer.default_encoding = 'ascii'

        engine = renderer._make_render_engine()
        literal = engine.literal

        self.assertEquals(literal(u"foo"), "foo")

    def test__literal__returns_unicode(self):
        """
        Test that literal returns unicode (and not a subclass).

        """
        renderer = Renderer()
        renderer.default_encoding = 'ascii'

        engine = renderer._make_render_engine()
        literal = engine.literal

        self.assertEquals(type(literal("foo")), unicode)

        class MyUnicode(unicode):
            pass

        s = MyUnicode("abc")

        self.assertEquals(type(s), MyUnicode)
        self.assertTrue(isinstance(s, unicode))
        self.assertEquals(type(literal(s)), unicode)

    ## Test the engine's escape attribute.

    def test__escape__uses_renderer_escape(self):
        """
        Test that escape uses the renderer's escape function.

        """
        renderer = Renderer()
        renderer.escape = lambda s: "**" + s

        engine = renderer._make_render_engine()
        escape = engine.escape

        self.assertEquals(escape("foo"), "**foo")

    def test__escape__uses_renderer_unicode(self):
        """
        Test that escape uses the renderer's unicode function.

        """
        renderer = Renderer()
        renderer.unicode = lambda s: s.upper()

        engine = renderer._make_render_engine()
        escape = engine.escape

        self.assertEquals(escape("foo"), "FOO")

    def test__escape__has_access_to_original_unicode_subclass(self):
        """
        Test that escape receives strings with the unicode subclass intact.

        """
        renderer = Renderer()
        renderer.escape = lambda s: type(s).__name__

        engine = renderer._make_render_engine()
        escape = engine.escape

        class MyUnicode(unicode):
            pass

        self.assertEquals(escape("foo"), "unicode")
        self.assertEquals(escape(u"foo"), "unicode")
        self.assertEquals(escape(MyUnicode("foo")), "MyUnicode")

    def test__escape__returns_unicode(self):
        """
        Test that literal returns unicode (and not a subclass).

        """
        renderer = Renderer()
        renderer.default_encoding = 'ascii'

        engine = renderer._make_render_engine()
        escape = engine.escape

        self.assertEquals(type(escape("foo")), unicode)

        # Check that literal doesn't preserve unicode subclasses.
        class MyUnicode(unicode):
            pass

        s = MyUnicode("abc")

        self.assertEquals(type(s), MyUnicode)
        self.assertTrue(isinstance(s, unicode))
        self.assertEquals(type(escape(s)), unicode)

