import unittest
import pystache

from examples.simple import Simple
from examples.complex_view import ComplexView
from examples.lambdas import Lambdas
from examples.inverted import Inverted

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

    def test_template_load_from_multiple_path(self):
        path = Simple.template_path
        Simple.template_path = ('examples/nowhere','examples',)
        try:
            view = Simple(thing='world')
            self.assertEquals(view.render(), "Hi world!")
        finally:
            Simple.template_path = path

    def test_template_load_from_multiple_path_fail(self):
        path = Simple.template_path
        Simple.template_path = ('examples/nowhere',)
        try:
            view = Simple(thing='world')
            self.assertRaises(IOError, view.render)
        finally:
            Simple.template_path = path

    def test_basic_method_calls(self):
        view = Simple()
        self.assertEquals(view.render(), "Hi pizza!")

    def test_non_callable_attributes(self):
        view = Simple()
        view.thing = 'Chris'
        self.assertEquals(view.render(), "Hi Chris!")

    def test_view_instances_as_attributes(self):
        other = Simple(name='chris')
        other.template = '{{name}}'
        view = Simple()
        view.thing = other
        self.assertEquals(view.render(), "Hi chris!")

    def test_complex(self):
        self.assertEquals(ComplexView().render(), """<h1>Colors</h1>
<ul>
  <li><strong>red</strong></li>\n    \n    <li><a href="#Green">green</a></li>
    <li><a href="#Blue">blue</a></li>
  </ul>
""")

    def test_higher_order_replace(self):
        view = Lambdas()
        self.assertEquals(view.render(),
                          'bar != bar. oh, it does!')

    def test_higher_order_rot13(self):
        view = Lambdas()
        view.template = '{{#rot13}}abcdefghijklm{{/rot13}}'
        self.assertEquals(view.render(), 'nopqrstuvwxyz')

    def test_higher_order_lambda(self):
        view = Lambdas()
        view.template = '{{#sort}}zyxwvutsrqponmlkjihgfedcba{{/sort}}'
        self.assertEquals(view.render(), 'abcdefghijklmnopqrstuvwxyz')

    def test_inverted(self):
        view = Inverted()
        self.assertEquals(view.render(), """one, two, three""")


if __name__ == '__main__':
    unittest.main()
