# encoding: utf-8

import unittest

from examples.comments import Comments
from examples.double_section import DoubleSection
from examples.escaped import Escaped
from examples.unescaped import Unescaped
from examples.template_partial import TemplatePartial
from examples.delimiters import Delimiters
from examples.unicode_output import UnicodeOutput
from examples.unicode_input import UnicodeInput
from examples.nested_context import NestedContext
from pystache import Renderer
from tests.common import AssertStringMixin


class TestView(unittest.TestCase, AssertStringMixin):

    def _assert(self, obj, expected):
        renderer = Renderer()
        actual = renderer.render(obj)
        self.assertString(actual, expected)

    def test_comments(self):
        self._assert(Comments(), u"<h1>A Comedy of Errors</h1>")

    def test_double_section(self):
        self._assert(DoubleSection(), u"* first\n* second\n* third")

    def test_unicode_output(self):
        self.assertEquals(UnicodeOutput().render(), u'<p>Name: Henri Poincaré</p>')

    def test_unicode_input(self):
        self.assertEquals(UnicodeInput().render(),
            u'<p>If alive today, Henri Poincaré would be 156 years old.</p>')

    def test_escaping(self):
        self._assert(Escaped(), u"<h1>Bear &gt; Shark</h1>")

    def test_literal(self):
        self.assertEquals(Unescaped().render(), "<h1>Bear > Shark</h1>")

    def test_template_partial(self):
        self.assertEquals(TemplatePartial().render(), """<h1>Welcome</h1>
Again, Welcome!""")

    def test_template_partial_extension(self):
        view = TemplatePartial()
        view.template_extension = 'txt'
        self.assertString(view.render(), u"""Welcome
-------

## Again, Welcome! ##""")

    def test_delimiters(self):
        renderer = Renderer()
        actual = renderer.render(Delimiters())
        self.assertString(actual, u"""\
* It worked the first time.
* And it worked the second time.
* Then, surprisingly, it worked the third time.
""")

    def test_nested_context(self):
        renderer = Renderer()
        actual = renderer.render(NestedContext(renderer))
        self.assertString(actual, u"one and foo and two")

    def test_nested_context_is_available_in_view(self):
        renderer = Renderer()

        view = NestedContext(renderer)
        view.template = '{{#herp}}{{#derp}}{{nested_context_in_view}}{{/derp}}{{/herp}}'

        actual = renderer.render(view)
        self.assertString(actual, u'it works!')

    def test_partial_in_partial_has_access_to_grand_parent_context(self):
        view = TemplatePartial(context = {'prop': 'derp'})
        view.template = '''{{>partial_in_partial}}'''
        self.assertEquals(view.render(), 'Hi derp!')

if __name__ == '__main__':
    unittest.main()
