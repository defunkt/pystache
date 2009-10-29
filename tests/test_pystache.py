import unittest
from pystache import Pystache

class TestPystache(unittest.TestCase):
    def test_basic(self):
        ret = Pystache.render("Hi {{thing}}!", { 'thing': 'world' })
        self.assertEquals(ret, "Hi world!")

    def test_less_basic(self):
        template = "It's a nice day for {{beverage}}, right {{person}}?"
        ret = Pystache.render(template, { 'beverage': 'soda', 'person': 'Bob' })
        self.assertEquals(ret, "It's a nice day for soda, right Bob?")

    def test_even_less_basic(self):
        template = "I think {{name}} wants a {{thing}}, right {{name}}?"
        ret = Pystache.render(template, { 'name': 'Jon', 'thing': 'racecar' })
        self.assertEquals(ret, "I think Jon wants a racecar, right Jon?")

    def test_comments(self):
        template = "What {{! the }} what?"
        ret = Pystache.render(template)
        self.assertEquals(ret, "What  what?")

    def xtest_sections(self):
        template = "I think {{name}} wants a {{thing}}, right {{name}}?"
        ret = Pystache.render(template, { 'name': 'Jon', 'thing': 'racecar' })
        self.assertEquals(ret, "I think Jon wants a racecar, right Jon?")
