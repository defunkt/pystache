import unittest
import pystache
from examples.simple import Simple

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
