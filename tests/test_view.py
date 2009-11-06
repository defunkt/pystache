import unittest
import pystache
from examples.simple import Simple
from examples.complex_view import ComplexView

class TestView(unittest.TestCase):
    def test_basic(self):
        view = Simple("Hi {{thing}}!", { 'thing': 'world' })
        self.assertEquals(view.render(), "Hi world!")

    def test_kwargs(self):
        view = Simple("Hi {{thing}}!", thing='world')
        self.assertEquals(view.render(), "Hi world!")

    def test_template_load(self):
        view = Simple(thing='world')
        self.assertEquals(view.render(), "Hi world!")

    def test_basic_method_calls(self):
        view = Simple()
        self.assertEquals(view.render(), "Hi pizza!")

    def test_complex(self):
        self.assertEquals(ComplexView().render(), """<h1>Colors</h1>
<ul>
  <li><strong>red</strong></li>
    <li><a href="#Green">green</a></li>
    <li><a href="#Blue">blue</a></li>
    </ul>
""")
