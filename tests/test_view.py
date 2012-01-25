# coding: utf-8

"""
Unit tests of view.py.

"""

import os.path
import unittest

from examples.simple import Simple
from examples.complex_view import ComplexView
from examples.lambdas import Lambdas
from examples.inverted import Inverted, InvertedLists
from pystache.reader import Reader
from pystache.view import View
from pystache.view import Locator as ViewLocator
from .common import AssertIsMixin
from .common import DATA_DIR
from .data.views import SampleView
from .data.views import NonAscii


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
        locator = ViewLocator(search_dirs=[DATA_DIR])
        return locator

    # TODO: fully test constructor.
    def test_init__reader(self):
        reader = "reader"  # in practice, this is a reader instance.
        locator = ViewLocator(search_dirs=None, template_locator=None, reader=reader)

        self.assertIs(locator.reader, reader)

    def _assert_template_location(self, view, expected):
        locator = self._make_locator()
        actual = locator.get_relative_template_location(view)
        self.assertEquals(actual, expected)

    def test_get_relative_template_location(self):
        """
        Test get_relative_template_location(): default behavior (no attributes set).

        """
        view = SampleView()
        self._assert_template_location(view, (None, 'sample_view.mustache'))

    def test_get_relative_template_location__template_path__file_name_only(self):
        """
        Test get_relative_template_location(): template_path attribute.

        """
        view = SampleView()
        view.template_path = 'template.txt'
        self._assert_template_location(view, ('', 'template.txt'))

    def test_get_relative_template_location__template_path__file_name_with_directory(self):
        """
        Test get_relative_template_location(): template_path attribute.

        """
        view = SampleView()
        view.template_path = 'foo/bar/template.txt'
        self._assert_template_location(view, ('foo/bar', 'template.txt'))

    def test_get_relative_template_location__template_name(self):
        """
        Test get_relative_template_location(): template_name attribute.

        """
        view = SampleView()
        view.template_name = 'new_name'
        self._assert_template_location(view, (None, 'new_name.mustache'))

    def test_get_relative_template_location__template_extension(self):
        """
        Test get_relative_template_location(): template_extension attribute.

        """
        view = SampleView()
        view.template_extension = 'txt'
        self._assert_template_location(view, (None, 'sample_view.txt'))

    def test_get_template_path__with_directory(self):
        """
        Test get_template_path() with a view that has a directory specified.

        """
        locator = self._make_locator()

        view = SampleView()
        view.template_path = 'foo/bar.txt'
        self.assertTrue(locator.get_relative_template_location(view)[0] is not None)

        actual = locator.get_template_path(view)
        expected = os.path.abspath(os.path.join(DATA_DIR, 'foo/bar.txt'))

        self.assertEquals(actual, expected)

    def test_get_template_path__without_directory(self):
        """
        Test get_template_path() with a view that doesn't have a directory specified.

        """
        locator = self._make_locator()

        view = SampleView()
        self.assertTrue(locator.get_relative_template_location(view)[0] is None)

        actual = locator.get_template_path(view)
        expected = os.path.abspath(os.path.join(DATA_DIR, 'sample_view.mustache'))

        self.assertEquals(actual, expected)

    def _assert_get_template(self, view, expected):
        locator = self._make_locator()
        actual = locator.get_template(view)

        self.assertEquals(type(actual), unicode)
        self.assertEquals(actual, expected)

    def test_get_template(self):
        """
        Test get_template(): default behavior (no attributes set).

        """
        view = SampleView()

        self._assert_get_template(view, u"ascii: abc")

    def test_get_template__template(self):
        """
        Test get_template(): template attribute.

        """
        view = SampleView()
        view.template = 'foo'

        self._assert_get_template(view, 'foo')

    def test_get_template__template__template_encoding(self):
        """
        Test get_template(): template attribute with template encoding attribute.

        """
        view = SampleView()
        view.template = u'é'.encode('utf-8')

        self.assertRaises(UnicodeDecodeError, self._assert_get_template, view, 'foo')

        view.template_encoding = 'utf-8'
        self._assert_get_template(view, u'é')

    def test_get_template__template_encoding(self):
        """
        Test get_template(): template_encoding attribute.

        """
        view = NonAscii()

        self.assertRaises(UnicodeDecodeError, self._assert_get_template, view, 'foo')

        view.template_encoding = 'utf-8'
        self._assert_get_template(view, u"non-ascii: é")
