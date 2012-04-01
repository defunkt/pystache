# coding: utf-8

"""
Unit tests for template_spec.py.

"""

import os.path
import sys
import unittest

from examples.simple import Simple
from examples.complex_view import ComplexView
from examples.lambdas import Lambdas
from examples.inverted import Inverted, InvertedLists
from pystache import TemplateSpec as Template
from pystache import Renderer
from pystache import View
from pystache.template_spec import SpecLoader
from pystache.locator import Locator
from pystache.loader import Loader
from .common import AssertIsMixin
from .common import AssertStringMixin
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
        Test that View.template_rel_path is respected for partials.

        """
        class TestView(View):
            template = "Partial: {{>tagless}}"

        view = TestView()
        self.assertRaises(IOError, view.render)

        view = TestView()
        view.template_path = "examples"
        self.assertEquals(view.render(), "Partial: No tags...")

    def test_basic_method_calls(self):
        view = Simple()
        self.assertEquals(view.render(), "Hi pizza!")

    def test_non_callable_attributes(self):
        view = Simple()
        view.thing = 'Chris'
        self.assertEquals(view.render(), "Hi Chris!")

    def test_complex(self):
        renderer = Renderer()
        expected = renderer.render(ComplexView())
        self.assertEquals(expected, """\
<h1>Colors</h1>
<ul>
<li><strong>red</strong></li>
<li><a href="#Green">green</a></li>
<li><a href="#Blue">blue</a></li>
</ul>""")

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


class SpecLoaderTests(unittest.TestCase, AssertIsMixin, AssertStringMixin):

    """
    Tests template_spec.SpecLoader.

    """

    def test_init__defaults(self):
        custom = SpecLoader()

        # Check the loader attribute.
        loader = custom.loader
        self.assertEquals(loader.extension, 'mustache')
        self.assertEquals(loader.file_encoding, sys.getdefaultencoding())
        to_unicode = loader.to_unicode

        # Check search_dirs.
        self.assertEquals(custom.search_dirs, [])

    def test_init__search_dirs(self):
        search_dirs = ['a', 'b']
        loader = SpecLoader(search_dirs)

        self.assertEquals(loader.search_dirs, ['a', 'b'])

    def test_init__loader(self):
        loader = Loader()
        custom = SpecLoader([], loader=loader)

        self.assertIs(custom.loader, loader)

    # TODO: rename to something like _assert_load().
    def _assert_template(self, loader, custom, expected):
        self.assertString(loader.load(custom), expected)

    def test_load__template__type_str(self):
        """
        Test the template attribute: str string.

        """
        custom = Template()
        custom.template = "abc"

        self._assert_template(SpecLoader(), custom, u"abc")

    def test_load__template__type_unicode(self):
        """
        Test the template attribute: unicode string.

        """
        custom = Template()
        custom.template = u"abc"

        self._assert_template(SpecLoader(), custom, u"abc")

    def test_load__template__unicode_non_ascii(self):
        """
        Test the template attribute: non-ascii unicode string.

        """
        custom = Template()
        custom.template = u"é"

        self._assert_template(SpecLoader(), custom, u"é")

    def test_load__template__with_template_encoding(self):
        """
        Test the template attribute: with template encoding attribute.

        """
        custom = Template()
        custom.template = u'é'.encode('utf-8')

        self.assertRaises(UnicodeDecodeError, self._assert_template, SpecLoader(), custom, u'é')

        custom.template_encoding = 'utf-8'
        self._assert_template(SpecLoader(), custom, u'é')

    # TODO: make this test complete.
    def test_load__template__correct_loader(self):
        """
        Test that reader.unicode() is called correctly.

        This test tests that the correct reader is called with the correct
        arguments.  This is a catch-all test to supplement the other
        test cases.  It tests SpecLoader.load() independent of reader.unicode()
        being implemented correctly (and tested).

        """
        class MockLoader(Loader):

            def __init__(self):
                self.s = None
                self.encoding = None

            # Overrides the existing method.
            def unicode(self, s, encoding=None):
                self.s = s
                self.encoding = encoding
                return u"foo"

        loader = MockLoader()
        custom_loader = SpecLoader()
        custom_loader.loader = loader

        view = Template()
        view.template = "template-foo"
        view.template_encoding = "encoding-foo"

        # Check that our unicode() above was called.
        self._assert_template(custom_loader, view, u'foo')
        self.assertEquals(loader.s, "template-foo")
        self.assertEquals(loader.encoding, "encoding-foo")


# TODO: migrate these tests into the SpecLoaderTests class.
# TODO: rename the get_template() tests to test load().
# TODO: condense, reorganize, and rename the tests so that it is
#   clear whether we have full test coverage (e.g. organized by
#   TemplateSpec attributes or something).
class TemplateSpecTests(unittest.TestCase):

    # TODO: rename this method to _make_loader().
    def _make_locator(self):
        locator = SpecLoader(search_dirs=[DATA_DIR])
        return locator

    def _assert_template_location(self, view, expected):
        locator = self._make_locator()
        actual = locator._find_relative(view)
        self.assertEquals(actual, expected)

    def test_find_relative(self):
        """
        Test _find_relative(): default behavior (no attributes set).

        """
        view = SampleView()
        self._assert_template_location(view, (None, 'sample_view.mustache'))

    def test_find_relative__template_rel_path__file_name_only(self):
        """
        Test _find_relative(): template_rel_path attribute.

        """
        view = SampleView()
        view.template_rel_path = 'template.txt'
        self._assert_template_location(view, ('', 'template.txt'))

    def test_find_relative__template_rel_path__file_name_with_directory(self):
        """
        Test _find_relative(): template_rel_path attribute.

        """
        view = SampleView()
        view.template_rel_path = 'foo/bar/template.txt'
        self._assert_template_location(view, ('foo/bar', 'template.txt'))

    def test_find_relative__template_rel_directory(self):
        """
        Test _find_relative(): template_rel_directory attribute.

        """
        view = SampleView()
        view.template_rel_directory = 'foo'

        self._assert_template_location(view, ('foo', 'sample_view.mustache'))

    def test_find_relative__template_name(self):
        """
        Test _find_relative(): template_name attribute.

        """
        view = SampleView()
        view.template_name = 'new_name'
        self._assert_template_location(view, (None, 'new_name.mustache'))

    def test_find_relative__template_extension(self):
        """
        Test _find_relative(): template_extension attribute.

        """
        view = SampleView()
        view.template_extension = 'txt'
        self._assert_template_location(view, (None, 'sample_view.txt'))

    def test_find__with_directory(self):
        """
        Test _find() with a view that has a directory specified.

        """
        locator = self._make_locator()

        view = SampleView()
        view.template_rel_path = 'foo/bar.txt'
        self.assertTrue(locator._find_relative(view)[0] is not None)

        actual = locator._find(view)
        expected = os.path.abspath(os.path.join(DATA_DIR, 'foo/bar.txt'))

        self.assertEquals(actual, expected)

    def test_find__without_directory(self):
        """
        Test _find() with a view that doesn't have a directory specified.

        """
        locator = self._make_locator()

        view = SampleView()
        self.assertTrue(locator._find_relative(view)[0] is None)

        actual = locator._find(view)
        expected = os.path.abspath(os.path.join(DATA_DIR, 'sample_view.mustache'))

        self.assertEquals(actual, expected)

    def _assert_get_template(self, custom, expected):
        locator = self._make_locator()
        actual = locator.load(custom)

        self.assertEquals(type(actual), unicode)
        self.assertEquals(actual, expected)

    def test_get_template(self):
        """
        Test get_template(): default behavior (no attributes set).

        """
        view = SampleView()

        self._assert_get_template(view, u"ascii: abc")

    def test_get_template__template_encoding(self):
        """
        Test get_template(): template_encoding attribute.

        """
        view = NonAscii()

        self.assertRaises(UnicodeDecodeError, self._assert_get_template, view, 'foo')

        view.template_encoding = 'utf-8'
        self._assert_get_template(view, u"non-ascii: é")
