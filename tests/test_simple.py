import unittest
import pystache
from examples.nested_context import NestedContext
from examples.complex_view import ComplexView
from examples.lambdas import Lambdas

class TestSimple(unittest.TestCase):
    
    def test_simple_render(self):
        tmpl = '{{derp}}'
        
        self.assertEqual('herp', pystache.Template(tmpl, {'derp': 'herp'}).render())
        
    def test_nested_context(self):
        view = NestedContext()
        self.assertEquals(pystache.Template('{{#foo}}{{thing1}} and {{thing2}} and {{outer_thing}}{{/foo}}{{^foo}}Not foo!{{/foo}}', view).render(), "one and foo and two")
        
    def test_looping_and_negation_context(self):
        view = ComplexView()
        self.assertEquals(pystache.Template('{{#item}}{{header}}: {{name}} {{/item}}{{^item}} Shouldnt see me{{/item}}', view).render(), "Colors: red Colors: green Colors: blue ")

    def test_empty_context(self):
        view = ComplexView()
        self.assertEquals(pystache.Template('{{#empty_list}}Shouldnt see me {{/empty_list}}{{^empty_list}}Should see me{{/empty_list}}', view).render(), "Should see me")
        
    def test_callables(self):
        view = Lambdas()
        self.assertEquals(pystache.Template('{{#replace_foo_with_bar}}foo != bar. oh, it does!{{/replace_foo_with_bar}}', view).render(), 'bar != bar. oh, it does!')