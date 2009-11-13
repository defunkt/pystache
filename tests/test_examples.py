import unittest
import pystache

from examples.comments import Comments

class TestView(unittest.TestCase):
    def test_comments(self):
        self.assertEquals(Comments().render(), """<h1>A Comedy of Errors</h1>
""")
