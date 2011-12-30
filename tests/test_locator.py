# encoding: utf-8

"""
Contains locator.py unit tests.

"""

import os
import sys
import unittest

from pystache.locator import Locator
from pystache.reader import Reader

from .common import DATA_DIR


class LocatorTests(unittest.TestCase):

    search_dirs = 'examples'

    def _locator(self):
        return Locator(search_dirs=DATA_DIR)

    def test_init__extension(self):
        # Test the default value.
        locator = Locator()
        self.assertEquals(locator.template_extension, 'mustache')

        locator = Locator(extension='txt')
        self.assertEquals(locator.template_extension, 'txt')

        locator = Locator(extension=False)
        self.assertTrue(locator.template_extension is False)

    def test_get_object_directory(self):
        locator = Locator()

        reader = Reader()
        actual = locator.get_object_directory(reader)

        expected = os.path.join(os.path.dirname(__file__), os.pardir, 'pystache')

        self.assertEquals(os.path.normpath(actual), os.path.normpath(expected))

    def test_make_file_name(self):
        locator = Locator()

        locator.template_extension = 'bar'
        self.assertEquals(locator.make_file_name('foo'), 'foo.bar')

        locator.template_extension = False
        self.assertEquals(locator.make_file_name('foo'), 'foo')

        locator.template_extension = ''
        self.assertEquals(locator.make_file_name('foo'), 'foo.')

    def test_locate_path(self):
        locator = Locator()
        path = locator.locate_path('simple', search_dirs=['examples'])

        self.assertEquals(os.path.basename(path), 'simple.mustache')

    def test_locate_path__using_list_of_paths(self):
        locator = Locator()
        path = locator.locate_path('simple', search_dirs=['doesnt_exist', 'examples'])

        self.assertTrue(path)

    def test_locate_path__precedence(self):
        """
        Test the order in which locate_path() searches directories.

        """
        locator = Locator()

        dir1 = DATA_DIR
        dir2 = os.path.join(DATA_DIR, 'locator')

        self.assertTrue(locator.locate_path('duplicate', search_dirs=[dir1]))
        self.assertTrue(locator.locate_path('duplicate', search_dirs=[dir2]))

        path = locator.locate_path('duplicate', search_dirs=[dir2, dir1])
        dirpath = os.path.dirname(path)
        dirname = os.path.split(dirpath)[-1]

        self.assertEquals(dirname, 'locator')

    def test_locate_path__non_existent_template_fails(self):
        locator = Locator()

        self.assertRaises(IOError, locator.locate_path, 'doesnt_exist', search_dirs=[])

    def test_make_template_name(self):
        """
        Test make_template_name().

        """
        locator = Locator()

        class FooBar(object):
            pass
        foo = FooBar()

        self.assertEquals(locator.make_template_name(foo), 'foo_bar')
