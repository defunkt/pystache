import unittest
from pystache import Pystache

class TestPystache(unittest.TestCase):
    def test_basic(self):
        ret = Pystache.render("Hi {{thing}}!", { 'thing': 'world' })
        self.assertEquals(ret, "Hi world!")

    def test_less_basic(self):
        template = """It's a nice day for {{beverage}}, right {{person}}?"""
        ret = Pystache.render(template, { 'beverage': 'soda', 'person': 'Bob' })
        self.assertEquals(ret, "It's a nice day for soda, right Bob?")


