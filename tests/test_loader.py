# encoding: utf-8

"""
Contains loader.py unit tests.

"""

import os
import sys
import unittest

from pystache.loader import make_template_name
from pystache.loader import Locator
from pystache.reader import Reader

from .common import DATA_DIR


class MakeTemplateNameTests(unittest.TestCase):

    """
    Test the make_template_name() function.

    """

    def test(self):
        class FooBar(object):
            pass
        foo = FooBar()
        self.assertEquals(make_template_name(foo), 'foo_bar')


class LocatorTests(unittest.TestCase):

    search_dirs = 'examples'

    def _locator(self):
        return Locator(search_dirs=DATA_DIR)

    def test_init__search_dirs(self):
        # Test the default value.
        locator = Locator()
        self.assertEquals(locator.search_dirs, [os.curdir])

        locator = Locator(search_dirs=['foo'])
        self.assertEquals(locator.search_dirs, ['foo'])

    def test_init__extension(self):
        # Test the default value.
        locator = Locator()
        self.assertEquals(locator.template_extension, 'mustache')

        locator = Locator(extension='txt')
        self.assertEquals(locator.template_extension, 'txt')

        locator = Locator(extension=False)
        self.assertTrue(locator.template_extension is False)

    def test_make_file_name(self):
        locator = Locator()

        locator.template_extension = 'bar'
        self.assertEquals(locator.make_file_name('foo'), 'foo.bar')

        locator.template_extension = False
        self.assertEquals(locator.make_file_name('foo'), 'foo')

        locator.template_extension = ''
        self.assertEquals(locator.make_file_name('foo'), 'foo.')

    def test_locate_path(self):
        locator = Locator(search_dirs='examples')
        path = locator.locate_path('simple')

        self.assertEquals(os.path.basename(path), 'simple.mustache')

    def test_locate_path__using_list_of_paths(self):
        locator = Locator(search_dirs=['doesnt_exist', 'examples'])
        path = locator.locate_path('simple')

        self.assertTrue(path)

    def test_locate_path__precedence(self):
        """
        Test the order in which locate_path() searches directories.

        """
        locator = Locator()

        dir1 = DATA_DIR
        dir2 = os.path.join(DATA_DIR, 'locator')

        locator.search_dirs = [dir1]
        self.assertTrue(locator.locate_path('duplicate'))
        locator.search_dirs = [dir2]
        self.assertTrue(locator.locate_path('duplicate'))

        locator.search_dirs = [dir2, dir1]
        path = locator.locate_path('duplicate')
        dirpath = os.path.dirname(path)
        dirname = os.path.split(dirpath)[-1]

        self.assertEquals(dirname, 'locator')

    def test_locate_path__non_existent_template_fails(self):
        locator = Locator()

        self.assertRaises(IOError, locator.locate_path, 'doesnt_exist')

