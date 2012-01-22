# coding: utf-8

"""
Unit tests of renderengine.py.

"""

import cgi
import unittest

from pystache.context import Context
from pystache.parser import ParsingError
from pystache.renderengine import RenderEngine
from tests.common import assert_strings


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


class RenderTests(unittest.TestCase):

    """
    Tests RenderEngine.render().

    Explicit spec-test-like tests best go in this class since the
    RenderEngine class contains all parsing logic.  This way, the unit tests
    will be more focused and fail "closer to the code".

    """

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

        assert_strings(test_case=self, actual=actual, expected=expected)

    def test_render(self):
        self._assert_render('Hi Mom', 'Hi {{person}}', {'person': 'Mom'})

    def test__load_partial(self):
        """
        Test that render() uses the load_template attribute.

        """
        engine = self._engine()
        partials = {'partial': u"{{person}}"}
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

    def test_tag__output_not_interpolated(self):
        """
        Context values should not be treated as templates (issue #44).

        """
        template = '{{template}}: {{planet}}'
        context = {'template': '{{planet}}', 'planet': 'Earth'}
        self._assert_render(u'{{planet}}: Earth', template, context)

    def test_tag__output_not_interpolated__section(self):
        """
        Context values should not be treated as templates (issue #44).

        """
        template = '{{test}}'
        context = {'test': '{{#hello}}'}
        self._assert_render('{{#hello}}', template, context)

    def test_interpolation__built_in_type__string(self):
        """
        Check tag interpolation with a string on the top of the context stack.

        """
        item = 'abc'
        # item.upper() == 'ABC'
        template = '{{#section}}{{upper}}{{/section}}'
        context = {'section': item, 'upper': 'XYZ'}
        self._assert_render(u'XYZ', template, context)

    def test_interpolation__built_in_type__integer(self):
        """
        Check tag interpolation with an integer on the top of the context stack.

        """
        item = 10
        # item.real == 10
        template = '{{#section}}{{real}}{{/section}}'
        context = {'section': item, 'real': 1000}
        self._assert_render(u'1000', template, context)

    def test_interpolation__built_in_type__list(self):
        """
        Check tag interpolation with a list on the top of the context stack.

        """
        item = [[1, 2, 3]]
        # item[0].pop() == 3
        template = '{{#section}}{{pop}}{{/section}}'
        context = {'section': item, 'pop': 7}
        self._assert_render(u'7', template, context)

    def test_implicit_iterator__literal(self):
        """
        Test an implicit iterator in a literal tag.

        """
        template = """{{#test}}{{{.}}}{{/test}}"""
        context = {'test': ['<', '>']}

        self._assert_render('<>', template, context)

    def test_implicit_iterator__escaped(self):
        """
        Test an implicit iterator in a normal tag.

        """
        template = """{{#test}}{{.}}{{/test}}"""
        context = {'test': ['<', '>']}

        self._assert_render('&lt;&gt;', template, context)

    def test_literal__in_section(self):
        """
        Check that literals work in sections.

        """
        template = '{{#test}}1 {{{less_than}}} 2{{/test}}'
        context = {'test': {'less_than': '<'}}

        self._assert_render('1 < 2', template, context)

    def test_literal__in_partial(self):
        """
        Check that literals work in partials.

        """
        template = '{{>partial}}'
        partials = {'partial': '1 {{{less_than}}} 2'}
        context = {'less_than': '<'}

        self._assert_render('1 < 2', template, context, partials=partials)

    def test_partial(self):
        partials = {'partial': "{{person}}"}
        self._assert_render('Hi Mom', 'Hi {{>partial}}', {'person': 'Mom'}, partials=partials)

    def test_partial__context_values(self):
        """
        Test that escape and literal work on context values in partials.

        """
        engine = self._engine()

        template = '{{>partial}}'
        partials = {'partial': 'unescaped: {{{foo}}} escaped: {{foo}}'}
        context = {'foo': '<'}

        self._assert_render('unescaped: < escaped: &lt;', template, context, engine=engine, partials=partials)

    ## Test cases related specifically to sections.

    def test_section__end_tag_with_no_start_tag(self):
        """
        Check what happens if there is an end tag with no start tag.

        """
        template = '{{/section}}'
        try:
            self._assert_render(None, template)
        except ParsingError, err:
            self.assertEquals(str(err), "Section end tag mismatch: u'section' != None")

    def test_section__end_tag_mismatch(self):
        """
        Check what happens if the end tag doesn't match.

        """
        template = '{{#section_start}}{{/section_end}}'
        try:
            self._assert_render(None, template)
        except ParsingError, err:
            self.assertEquals(str(err), "Section end tag mismatch: u'section_end' != u'section_start'")

    def test_section__context_values(self):
        """
        Test that escape and literal work on context values in sections.

        """
        engine = self._engine()

        template = '{{#test}}unescaped: {{{foo}}} escaped: {{foo}}{{/test}}'
        context = {'test': {'foo': '<'}}

        self._assert_render('unescaped: < escaped: &lt;', template, context, engine=engine)

    def test_section__context_precedence(self):
        """
        Check that items higher in the context stack take precedence.

        """
        template = '{{entree}} : {{#vegetarian}}{{entree}}{{/vegetarian}}'
        context = {'entree': 'chicken', 'vegetarian': {'entree': 'beans and rice'}}
        self._assert_render(u'chicken : beans and rice', template, context)

    def test_section__list_referencing_outer_context(self):
        """
        Check that list items can access the parent context.

        For sections whose value is a list, check that items in the list
        have access to the values inherited from the parent context
        when rendering.

        """
        context = {
            "greeting": "Hi",
            "list": [{"name": "Al"}, {"name": "Bob"}],
        }

        template = "{{#list}}{{greeting}} {{name}}, {{/list}}"

        self._assert_render("Hi Al, Hi Bob, ", template, context)

    def test_section__output_not_interpolated(self):
        """
        Check that rendered section output is not interpolated.

        """
        template = '{{#section}}{{template}}{{/section}}: {{planet}}'
        context = {'section': True, 'template': '{{planet}}', 'planet': 'Earth'}
        self._assert_render(u'{{planet}}: Earth', template, context)

    def test_section__nested_truthy(self):
        """
        Check that "nested truthy" sections get rendered.

        Test case for issue #24: https://github.com/defunkt/pystache/issues/24

        This test is copied from the spec.  We explicitly include it to
        prevent regressions for those who don't pull down the spec tests.

        """
        template = '| A {{#bool}}B {{#bool}}C{{/bool}} D{{/bool}} E |'
        context = {'bool': True}
        self._assert_render(u'| A B C D E |', template, context)

    def test_section__nested_with_same_keys(self):
        """
        Check a doubly-nested section with the same context key.

        Test case for issue #36: https://github.com/defunkt/pystache/issues/36

        """
        # Start with an easier, working case.
        template = '{{#x}}{{#z}}{{y}}{{/z}}{{/x}}'
        context = {'x': {'z': {'y': 1}}}
        self._assert_render(u'1', template, context)

        template = '{{#x}}{{#x}}{{y}}{{/x}}{{/x}}'
        context = {'x': {'x': {'y': 1}}}
        self._assert_render(u'1', template, context)

    def test_section__lambda(self):
        template = '{{#test}}Mom{{/test}}'
        context = {'test': (lambda text: 'Hi %s' % text)}
        self._assert_render('Hi Mom', template, context)

    def test_section__lambda__tag_in_output(self):
        """
        Check that callable output is treated as a template string (issue #46).

        The spec says--

            When used as the data value for a Section tag, the lambda MUST
            be treatable as an arity 1 function, and invoked as such (passing
            a String containing the unprocessed section contents).  The
            returned value MUST be rendered against the current delimiters,
            then interpolated in place of the section.

        """
        template = '{{#test}}Hi {{person}}{{/test}}'
        context = {'person': 'Mom', 'test': (lambda text: text + " :)")}
        self._assert_render('Hi Mom :)', template, context)

    def test_comment__multiline(self):
        """
        Check that multiline comments are permitted.

        """
        self._assert_render('foobar', 'foo{{! baz }}bar')
        self._assert_render('foobar', 'foo{{! \nbaz }}bar')

    def test_custom_delimiters__sections(self):
        """
        Check that custom delimiters can be used to start a section.

        Test case for issue #20: https://github.com/defunkt/pystache/issues/20

        """
        template = '{{=[[ ]]=}}[[#foo]]bar[[/foo]]'
        context = {'foo': True}
        self._assert_render(u'bar', template, context)

    def test_custom_delimiters__not_retroactive(self):
        """
        Check that changing custom delimiters back is not "retroactive."

        Test case for issue #35: https://github.com/defunkt/pystache/issues/35

        """
        expected = u' {{foo}} '
        self._assert_render(expected, '{{=$ $=}} {{foo}} ')
        self._assert_render(expected, '{{=$ $=}} {{foo}} $={{ }}=$')  # was yielding u'  '.
