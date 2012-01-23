import unittest
import pystache

from examples.simple import Simple
from examples.complex_view import ComplexView
from examples.lambdas import Lambdas
from examples.inverted import Inverted, InvertedLists
from pystache.view import View
from pystache.view import Locator
from tests.common import AssertIsMixin


class Thing(object):
    pass


class ViewTestCase(unittest.TestCase):

    def test_init(self):
        """
        Test the constructor.

        """
        class TestView(View):
            template = "foo"

        view = TestView()
        self.assertEquals(view.template, "foo")

    def test_init__kwargs_does_not_modify_context(self):
        """
        Test that passing **kwargs does not modify the passed context.

        """
        context = {"foo": "bar"}
        view = View(context=context, fuzz="buzz")
        self.assertEquals(context, {"foo": "bar"})

    def test_basic(self):
        view = Simple("Hi {{thing}}!", { 'thing': 'world' })
        self.assertEquals(view.render(), "Hi world!")

    def test_kwargs(self):
        view = Simple("Hi {{thing}}!", thing='world')
        self.assertEquals(view.render(), "Hi world!")

    def test_render(self):
        view = Simple(thing='world')
        self.assertEquals(view.render(), "Hi world!")

    def test_render__partials(self):
        """
        Test passing partials to View.__init__().

        """
        template = "{{>partial}}"
        partials = {"partial": "Loaded from dictionary"}
        view = Simple(template=template, partials=partials)
        actual = view.render()

        self.assertEquals(actual, "Loaded from dictionary")

    def test_template_path(self):
        """
        Test that View.template_path is respected.

        """
        class Tagless(View):
            pass

        view = Tagless()
        self.assertRaises(IOError, view.render)

        view = Tagless()
        view.template_path = "examples"
        self.assertEquals(view.render(), "No tags...")

    def test_template_path_for_partials(self):
        """
        Test that View.template_path is respected for partials.

        """
        class TestView(View):
            template = "Partial: {{>tagless}}"

        view = TestView()
        self.assertRaises(IOError, view.render)

        view = TestView()
        view.template_path = "examples"
        self.assertEquals(view.render(), "Partial: No tags...")

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

    def test_inverted_lists(self):
        view = InvertedLists()
        self.assertEquals(view.render(), """one, two, three, empty list""")


class LocatorTests(unittest.TestCase, AssertIsMixin):

    def _make_locator(self):
        class MockReader(object):
            def read(self, path):
                return "read: %s" % repr(path)

        reader = MockReader()
        locator = Locator(reader=reader)
        return locator

    def test_init__reader(self):
        reader = "reader"  # in practice, this is a reader instance.
        locator = Locator(reader)

        self.assertIs(locator.reader, reader)

    # TODO: make this test real
    def test_get_relative_template_location__template_path__file_name(self):
        locator = self._make_locator()
        view = View()

        view.template_path = 'foo.txt'
        self.assertEquals(locator.get_relative_template_location(view), ('', 'foo.txt'))

    # TODO: make this test real
    def test_get_relative_template_location__template_path__full_path(self):
        locator = self._make_locator()
        view = View()

        view.template_path = 'foo.txt'
        self.assertEquals(locator.get_relative_template_location(view), ('', 'foo.txt'))

    def test_get_template__template_attribute_set(self):
        """
        Test get_template() with view.template set to a non-None value.

        """
        locator = self._make_locator()
        view = View()
        view.template = 'foo'

        self.assertEquals(locator.get_template(view), 'foo')

    def test_get_template__template_attribute_not_set(self):
        """
        Test get_template() with view.template set to None.

        """
        locator = self._make_locator()
        locator.get_template_path = lambda view: "path"

        view = View()
        view.template = None

        self.assertEquals(locator.get_template(view), "read: 'path'")
