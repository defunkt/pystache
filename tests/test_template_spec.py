# coding: utf-8

"""
Unit tests for template_spec.py.

"""

from pystache.compat import *
import os.path
import sys
import unittest

import examples
from examples.simple import Simple
from examples.complex import Complex
from examples.lambdas import Lambdas
from examples.inverted import Inverted, InvertedLists
from pystache import Renderer
from pystache import TemplateSpec
from pystache.locator import Locator
from pystache.loader import Loader
from pystache.spec_loader import SpecLoader
from tests.common import DATA_DIR
from tests.common import EXAMPLES_DIR
from tests.common import AssertIsMixin
from tests.common import AssertStringMixin
from tests.data.views import SampleView
from tests.data.views import NonAscii


class Thing(object):
    pass


class ViewTestCase(unittest.TestCase, AssertStringMixin):

    def test_template_rel_directory(self):
        """
        Test that View.template_rel_directory is respected.

        """
        class Tagless(TemplateSpec):
            pass

        view = Tagless()
        renderer = Renderer()

        self.assertRaises(IOError, renderer.render, view)

        view.template_rel_directory = "../examples"
        actual = renderer.render(view)
        self.assertEquals(actual, "No tags...")

    def test_template_path_for_partials(self):
        """
        Test that View.template_rel_path is respected for partials.

        """
        spec = TemplateSpec()
        spec.template = "Partial: {{>tagless}}"

        renderer1 = Renderer()
        renderer2 = Renderer(search_dirs=EXAMPLES_DIR)

        self.assertRaises(IOError, renderer1.render, spec)

        actual = renderer2.render(spec)
        self.assertEquals(actual, "Partial: No tags...")

    def test_basic_method_calls(self):
        renderer = Renderer()
        actual = renderer.render(Simple())

        self.assertString(actual, u"Hi pizza!")

    def test_non_callable_attributes(self):
        view = Simple()
        view.thing = 'Chris'

        renderer = Renderer()
        actual = renderer.render(view)
        self.assertEquals(actual, "Hi Chris!")

    def test_complex(self):
        renderer = Renderer()
        actual = renderer.render(Complex())
        self.assertString(actual, u"""\
<h1>Colors</h1>
<ul>
<li><strong>red</strong></li>
<li><a href="#Green">green</a></li>
<li><a href="#Blue">blue</a></li>
</ul>""")

    def test_higher_order_replace(self):
        renderer = Renderer()
        actual = renderer.render(Lambdas())
        self.assertEquals(actual, 'bar != bar. oh, it does!')

    def test_higher_order_rot13(self):
        view = Lambdas()
        view.template = '{{#rot13}}abcdefghijklm{{/rot13}}'

        renderer = Renderer()
        actual = renderer.render(view)
        self.assertString(actual, u'nopqrstuvwxyz')

    def test_higher_order_lambda(self):
        view = Lambdas()
        view.template = '{{#sort}}zyxwvutsrqponmlkjihgfedcba{{/sort}}'

        renderer = Renderer()
        actual = renderer.render(view)
        self.assertString(actual, u'abcdefghijklmnopqrstuvwxyz')

    def test_partials_with_lambda(self):
        view = Lambdas()
        view.template = '{{>partial_with_lambda}}'

        renderer = Renderer(search_dirs=EXAMPLES_DIR)
        actual = renderer.render(view)
        self.assertEquals(actual, u'nopqrstuvwxyz')

    def test_hierarchical_partials_with_lambdas(self):
        view = Lambdas()
        view.template = '{{>partial_with_partial_and_lambda}}'

        renderer = Renderer(search_dirs=EXAMPLES_DIR)
        actual = renderer.render(view)
        self.assertString(actual, u'nopqrstuvwxyznopqrstuvwxyz')

    def test_inverted(self):
        renderer = Renderer()
        actual = renderer.render(Inverted())
        self.assertString(actual, u"""one, two, three, empty list""")

    def test_accessing_properties_on_parent_object_from_child_objects(self):
        parent = Thing()
        parent.this = 'derp'
        parent.children = [Thing()]
        view = Simple()
        view.template = "{{#parent}}{{#children}}{{this}}{{/children}}{{/parent}}"

        renderer = Renderer()
        actual = renderer.render(view, {'parent': parent})

        self.assertString(actual, u'derp')

    def test_inverted_lists(self):
        renderer = Renderer()
        actual = renderer.render(InvertedLists())
        self.assertString(actual, u"""one, two, three, empty list""")


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
        # TODO: finish testing the other Loader attributes.
        to_unicode = loader.to_unicode

    def test_init__loader(self):
        loader = Loader()
        custom = SpecLoader(loader=loader)

        self.assertIs(custom.loader, loader)

    # TODO: rename to something like _assert_load().
    def _assert_template(self, loader, custom, expected):
        self.assertString(loader.load(custom), expected)

    def test_load__template__type_str(self):
        """
        Test the template attribute: str string.

        """
        custom = TemplateSpec()
        custom.template = "abc"

        self._assert_template(SpecLoader(), custom, u"abc")

    def test_load__template__type_unicode(self):
        """
        Test the template attribute: unicode string.

        """
        custom = TemplateSpec()
        custom.template = u"abc"

        self._assert_template(SpecLoader(), custom, u"abc")

    def test_load__template__unicode_non_ascii(self):
        """
        Test the template attribute: non-ascii unicode string.

        """
        custom = TemplateSpec()
        custom.template = u"é"

        self._assert_template(SpecLoader(), custom, u"é")

    def test_load__template__with_template_encoding(self):
        """
        Test the template attribute: with template encoding attribute.

        """
        custom = TemplateSpec()
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

        view = TemplateSpec()
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
        return SpecLoader()

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
        self.assert_(locator._find_relative(view)[0] is not None)

        actual = locator._find(view)
        expected = os.path.abspath(os.path.join(DATA_DIR, 'foo/bar.txt'))

        self.assertEquals(actual, expected)

    def test_find__without_directory(self):
        """
        Test _find() with a view that doesn't have a directory specified.

        """
        locator = self._make_locator()

        view = SampleView()
        self.assert_(locator._find_relative(view)[0] is None)

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

if __name__ == '__main__':
    unittest.main()
