# coding: utf-8

"""
Unit tests of renderengine.py.

"""

import cgi
import unittest

from pystache.context import Context
from pystache.renderengine import RenderEngine


class RenderEngineTestCase(unittest.TestCase):

    """Test the RenderEngine class."""

    def test_init(self):
        """
        Test that __init__() stores all of the arguments correctly.

        """
        # In real-life, these arguments would be functions
        engine = RenderEngine(load_partial="foo", literal="literal", escape="escape")

        self.assertEquals(engine.escape, "escape")
        self.assertEquals(engine.literal, "literal")
        self.assertEquals(engine.load_partial, "foo")


class RenderEngineEnderTestCase(unittest.TestCase):

    """Test RenderEngine.render()."""

    def _engine(self):
        """
        Create and return a default RenderEngine for testing.

        """
        escape = lambda s: unicode(cgi.escape(s))
        engine = RenderEngine(literal=unicode, escape=escape, load_partial=None)
        return engine

    def _assert_render(self, expected, template, *context, **kwargs):
        """
        Test rendering the given template using the given context.

        """
        partials = kwargs.get('partials')
        engine = kwargs.get('engine', self._engine())

        if partials is not None:
            engine.load_partial = lambda key: unicode(partials[key])

        context = Context(*context)

        actual = engine.render(template, context)

        self.assertEquals(actual, expected)

    def test_render(self):
        self._assert_render('Hi Mom', 'Hi {{person}}', {'person': 'Mom'})

    def test__load_partial(self):
        """
        Test that render() uses the load_template attribute.

        """
        engine = self._engine()
        partials = {'partial': "{{person}}"}
        engine.load_partial = lambda key: partials[key]

        self._assert_render('Hi Mom', 'Hi {{>partial}}', {'person': 'Mom'}, engine=engine)

    def test__literal(self):
        """
        Test that render() uses the literal attribute.

        """
        engine = self._engine()
        engine.literal = lambda s: s.upper()

        self._assert_render('BAR', '{{{foo}}}', {'foo': 'bar'}, engine=engine)

    def test__escape(self):
        """
        Test that render() uses the escape attribute.

        """
        engine = self._engine()
        engine.escape = lambda s: "**" + s

        self._assert_render('**bar', '{{foo}}', {'foo': 'bar'}, engine=engine)

    def test__escape_does_not_call_literal(self):
        """
        Test that render() does not call literal before or after calling escape.

        """
        engine = self._engine()
        engine.literal = lambda s: s.upper()  # a test version
        engine.escape = lambda s: "**" + s

        template = 'literal: {{{foo}}} escaped: {{foo}}'
        context = {'foo': 'bar'}

        self._assert_render('literal: BAR escaped: **bar', template, context, engine=engine)

    def test__escape_preserves_unicode_subclasses(self):
        """
        Test that render() preserves unicode subclasses when passing to escape.

        This is useful, for example, if one wants to respect whether a
        variable value is markupsafe.Markup when escaping.

        """
        class MyUnicode(unicode):
            pass

        def escape(s):
            if type(s) is MyUnicode:
                return "**" + s
            else:
                return s + "**"

        engine = self._engine()
        engine.escape = escape

        template = '{{foo1}} {{foo2}}'
        context = {'foo1': MyUnicode('bar'), 'foo2': 'bar'}

        self._assert_render('**bar bar**', template, context, engine=engine)

    def test__non_basestring__literal_and_escaped(self):
        """
        Test a context value that is not a basestring instance.

        """
        # We use include upper() to make sure we are actually using
        # our custom function in the tests
        to_unicode = lambda s: unicode(s, encoding='ascii').upper()
        engine = self._engine()
        engine.escape = to_unicode
        engine.literal = to_unicode

        self.assertRaises(TypeError, engine.literal, 100)

        template = '{{text}} {{int}} {{{int}}}'
        context = {'int': 100, 'text': 'foo'}

        self._assert_render('FOO 100 100', template, context, engine=engine)

    def test__implicit_iterator__literal(self):
        """
        Test an implicit iterator in a literal tag.

        """
        template = """{{#test}}{{.}}{{/test}}"""
        context = {'test': ['a', 'b']}

        self._assert_render('ab', template, context)

    def test__implicit_iterator__escaped(self):
        """
        Test an implicit iterator in a normal tag.

        """
        template = """{{#test}}{{{.}}}{{/test}}"""
        context = {'test': ['a', 'b']}

        self._assert_render('ab', template, context)

    def test_render_with_partial(self):
        partials = {'partial': "{{person}}"}
        self._assert_render('Hi Mom', 'Hi {{>partial}}', {'person': 'Mom'}, partials=partials)

    def test_render__section_context_values(self):
        """
        Test that escape and literal work on context values in sections.

        """
        engine = self._engine()

        template = '{{#test}}unescaped: {{{foo}}} escaped: {{foo}}{{/test}}'
        context = {'test': {'foo': '<'}}

        self._assert_render('unescaped: < escaped: &lt;', template, context, engine=engine)

    def test_render__partial_context_values(self):
        """
        Test that escape and literal work on context values in partials.

        """
        engine = self._engine()

        template = '{{>partial}}'
        partials = {'partial': 'unescaped: {{{foo}}} escaped: {{foo}}'}
        context = {'foo': '<'}

        self._assert_render('unescaped: < escaped: &lt;', template, context, engine=engine, partials=partials)

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

        template = "{{#list}}{{name}}: {{greeting}}; {{/list}}"

        self._assert_render("Al: Hi; Bo: Hi; ", template, context)

    def test_render__tag_in_value(self):
        """
        Context values should not be treated as templates (issue #44).

        """
        template = '{{test}}'
        context = {'test': '{{hello}}'}
        self._assert_render('{{hello}}', template, context)

    def test_render__section_in_value(self):
        """
        Context values should not be treated as templates (issue #44).

        """
        template = '{{test}}'
        context = {'test': '{{#hello}}'}
        self._assert_render('{{#hello}}', template, context)

    def test_render__section__lambda(self):
        template = '{{#test}}Mom{{/test}}'
        context = {'test': (lambda text: 'Hi %s' % text)}
        self._assert_render('Hi Mom', template, context)

    def test_render__section__lambda__tag_in_output(self):
        """
        Check that callable output isn't treated as a template string (issue #46).

        """
        template = '{{#test}}Mom{{/test}}'
        context = {'test': (lambda text: '{{hi}} %s' % text)}
        self._assert_render('{{hi}} Mom', template, context)

    def test_render__section__comment__multiline(self):
        """
        Check that multiline comments are permitted.

        """
        self._assert_render('foobar', 'foo{{! baz }}bar')
        self._assert_render('foobar', 'foo{{! \nbaz }}bar')

