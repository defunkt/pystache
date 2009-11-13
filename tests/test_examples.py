import unittest
import pystache

from examples.comments import Comments
from examples.double_section import DoubleSection

class TestView(unittest.TestCase):
    def test_comments(self):
        self.assertEquals(Comments().render(), """<h1>A Comedy of Errors</h1>
""")

    def test_double_section(self):
        self.assertEquals(DoubleSection().render(), """* first
* second
* third""")
