# encoding: utf-8

"""
Contains locator.py unit tests.

"""

from datetime import datetime
import os
import sys
import unittest

from pystache.locator import Locator
from pystache.reader import Reader

from .common import DATA_DIR
from data.templates import SayHello

class LocatorTests(unittest.TestCase):

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

        obj = SayHello()
        actual = locator.get_object_directory(obj)

        self.assertEquals(actual, os.path.abspath(DATA_DIR))

    def test_get_object_directory__not_hasattr_module(self):
        locator = Locator()

        obj = datetime(2000, 1, 1)
        self.assertFalse(hasattr(obj, '__module__'))
        self.assertEquals(locator.get_object_directory(obj), None)

        self.assertFalse(hasattr(None, '__module__'))
        self.assertEquals(locator.get_object_directory(None), None)

    def test_make_file_name(self):
        locator = Locator()

        locator.template_extension = 'bar'
        self.assertEquals(locator.make_file_name('foo'), 'foo.bar')

        locator.template_extension = False
        self.assertEquals(locator.make_file_name('foo'), 'foo')

        locator.template_extension = ''
        self.assertEquals(locator.make_file_name('foo'), 'foo.')

    def test_find_path(self):
        locator = Locator()
        path = locator.find_path(search_dirs=['examples'], template_name='simple')

        self.assertEquals(os.path.basename(path), 'simple.mustache')

    def test_find_path__using_list_of_paths(self):
        locator = Locator()
        path = locator.find_path(search_dirs=['doesnt_exist', 'examples'], template_name='simple')

        self.assertTrue(path)

    def test_find_path__precedence(self):
        """
        Test the order in which find_path() searches directories.

        """
        locator = Locator()

        dir1 = DATA_DIR
        dir2 = os.path.join(DATA_DIR, 'locator')

        self.assertTrue(locator.find_path(search_dirs=[dir1], template_name='duplicate'))
        self.assertTrue(locator.find_path(search_dirs=[dir2], template_name='duplicate'))

        path = locator.find_path(search_dirs=[dir2, dir1], template_name='duplicate')
        dirpath = os.path.dirname(path)
        dirname = os.path.split(dirpath)[-1]

        self.assertEquals(dirname, 'locator')

    def test_find_path__non_existent_template_fails(self):
        locator = Locator()

        self.assertRaises(IOError, locator.find_path, search_dirs=[], template_name='doesnt_exist')

    def test_find_path_by_object(self):
        locator = Locator()

        obj = SayHello()

        actual = locator.find_path_by_object(search_dirs=[], template_name='say_hello', obj=obj)
        expected = os.path.abspath(os.path.join(DATA_DIR, 'say_hello.mustache'))

        self.assertEquals(actual, expected)

    def test_find_path_by_object__none_object_directory(self):
        locator = Locator()

        obj = None
        self.assertEquals(None, locator.get_object_directory(obj))

        actual = locator.find_path_by_object(search_dirs=[DATA_DIR], template_name='say_hello', obj=obj)
        expected = os.path.join(DATA_DIR, 'say_hello.mustache')

        self.assertEquals(actual, expected)

    def test_make_template_name(self):
        """
        Test make_template_name().

        """
        locator = Locator()

        class FooBar(object):
            pass
        foo = FooBar()

        self.assertEquals(locator.make_template_name(foo), 'foo_bar')
