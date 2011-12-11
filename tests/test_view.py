import unittest
import pystache

from examples.simple import Simple
from examples.complex_view import ComplexView
from examples.lambdas import Lambdas
from examples.inverted import Inverted, InvertedLists

class Thing(object):
    pass

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

    def test_load_template(self):
        """
        Test View.load_template().

        """
        template = Simple().load_template("escaped")
        self.assertEquals(template, "<h1>{{title}}</h1>")

    def test_custom_load_template(self):
        """
        Test passing a custom load_template to View.__init__().

        """
        partials_dict = {"partial": "Loaded from dictionary"}
        load_template = lambda template_name: partials_dict[template_name]

        view = Simple(load_template=load_template)

        actual = view.load_template("partial")
        self.assertEquals(actual, "Loaded from dictionary")

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
        self.assertEquals(ComplexView().render(),
            """<h1>Colors</h1><ul><li><strong>red</strong></li><li><a href="#Green">green</a></li><li><a href="#Blue">blue</a></li></ul>""")

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

    def test_partials_with_lambda(self):
        view = Lambdas()
        view.template = '{{>partial_with_lambda}}'
        self.assertEquals(view.render(), 'nopqrstuvwxyz')

    def test_hierarchical_partials_with_lambdas(self):
        view = Lambdas()
        view.template = '{{>partial_with_partial_and_lambda}}'
        self.assertEquals(view.render(), 'nopqrstuvwxyznopqrstuvwxyz')

    def test_inverted(self):
        view = Inverted()
        self.assertEquals(view.render(), """one, two, three, empty list""")

    def test_accessing_properties_on_parent_object_from_child_objects(self):
        parent = Thing()
        parent.this = 'derp'
        parent.children = [Thing()]
        view = Simple(context={'parent': parent})
        view.template = "{{#parent}}{{#children}}{{this}}{{/children}}{{/parent}}"

        self.assertEquals(view.render(), 'derp')

    def test_context_returns_a_flattened_dict(self):
        view = Simple()
        view.context_list = [{'one':'1'}, {'two':'2'}, object()]

        self.assertEqual(view.context, {'one': '1', 'two': '2'})

    def test_inverted_lists(self):
        view = InvertedLists()
        self.assertEquals(view.render(), """one, two, three, empty list""")

if __name__ == '__main__':
    unittest.main()
