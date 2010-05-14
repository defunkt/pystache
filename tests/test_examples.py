# encoding: utf-8

import unittest
import pystache

from examples.comments import Comments
from examples.double_section import DoubleSection
from examples.escaped import Escaped
from examples.unescaped import Unescaped
from examples.template_partial import TemplatePartial
from examples.delimiters import Delimiters
from examples.unicode_output import UnicodeOutput
from examples.unicode_input import UnicodeInput
from examples.nested_context import NestedContext

class TestView(unittest.TestCase):
    def test_comments(self):
        self.assertEquals(Comments().render(), """<h1>A Comedy of Errors</h1>
""")

    def test_double_section(self):
        self.assertEquals(DoubleSection().render(), """* first
* second
* third""")

    def test_unicode_output(self):
        self.assertEquals(UnicodeOutput().render(), u'<p>Name: Henri Poincaré</p>')

    def test_encoded_output(self):
        self.assertEquals(UnicodeOutput().render('utf8'), '<p>Name: Henri Poincar\xc3\xa9</p>')

    def test_unicode_input(self):
        self.assertEquals(UnicodeInput().render(),
            u'<p>If alive today, Henri Poincaré would be 156 years old.</p>')

    def test_escaped(self):
        self.assertEquals(Escaped().render(), "<h1>Bear &gt; Shark</h1>")

    def test_unescaped(self):
        self.assertEquals(Unescaped().render(), "<h1>Bear > Shark</h1>")

    def test_unescaped_sigil(self):
        view = Escaped(template="<h1>{{& thing}}</h1>", context={
                'thing': 'Bear > Giraffe'
                })
        self.assertEquals(view.render(), "<h1>Bear > Giraffe</h1>")

    def test_template_partial(self):
        self.assertEquals(TemplatePartial().render(), """<h1>Welcome</h1>
Again, Welcome!""")

    def test_template_partial_extension(self):
        view = TemplatePartial()
        view.template_extension = 'txt'
        self.assertEquals(view.render(), """Welcome
-------

Again, Welcome!
""")


    def test_delimiters(self):
        self.assertEquals(Delimiters().render(), """
* It worked the first time.

* And it worked the second time.

* Then, surprisingly, it worked the third time.
""")

    def test_nested_context(self):
        self.assertEquals(NestedContext().render(), "one and foo and two")

if __name__ == '__main__':
    unittest.main()
