import unittest
import pystache

from examples.comments import Comments
from examples.double_section import DoubleSection
from examples.escaped import Escaped
from examples.unescaped import Unescaped
from examples.template_partial import TemplatePartial

class TestView(unittest.TestCase):
    def test_comments(self):
        self.assertEquals(Comments().render(), """<h1>A Comedy of Errors</h1>
""")

    def test_double_section(self):
        self.assertEquals(DoubleSection().render(), """* first
* second
* third""")

    def test_escaped(self):
        self.assertEquals(Escaped().render(), "<h1>Bear &gt; Shark</h1>")

    def test_unescaped(self):
        self.assertEquals(Unescaped().render(), "<h1>Bear > Shark</h1>")

    def test_template_partial(self):
        self.assertEquals(TemplatePartial().render(), 'blah')
