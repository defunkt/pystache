import os
import sys
import unittest

from pystache.loader import Loader


class LoaderTestCase(unittest.TestCase):

    search_dirs = 'examples'

    def test_init__search_dirs(self):
        # Test the default value.
        loader = Loader()
        self.assertEquals(loader.search_dirs, [os.curdir])

        loader = Loader(search_dirs=['foo'])
        self.assertEquals(loader.search_dirs, ['foo'])

    def test_init__extension(self):
        # Test the default value.
        loader = Loader()
        self.assertEquals(loader.template_extension, 'mustache')

        loader = Loader(extension='txt')
        self.assertEquals(loader.template_extension, 'txt')

        loader = Loader(extension=False)
        self.assertTrue(loader.template_extension is False)

    def test_init__loader(self):
        # Test the default value.
        loader = Loader()
        self.assertEquals(loader.template_encoding, sys.getdefaultencoding())

        loader = Loader(encoding='foo')
        self.assertEquals(loader.template_encoding, 'foo')

    def test_make_file_name(self):
        loader = Loader()

        loader.template_extension = 'bar'
        self.assertEquals(loader.make_file_name('foo'), 'foo.bar')

        loader.template_extension = False
        self.assertEquals(loader.make_file_name('foo'), 'foo')

        loader.template_extension = ''
        self.assertEquals(loader.make_file_name('foo'), 'foo.')

    def test_get__template_is_loaded(self):
        loader = Loader(search_dirs='examples')
        template = loader.get('simple')

        self.assertEqual(template, 'Hi {{thing}}!{{blank}}')

    def test_get__using_list_of_paths(self):
        loader = Loader(search_dirs=['doesnt_exist', 'examples'])
        template = loader.get('simple')

        self.assertEqual(template, 'Hi {{thing}}!{{blank}}')

    def test_get__non_existent_template_fails(self):
        loader = Loader()

        self.assertRaises(IOError, loader.get, 'doesnt_exist')

    def test_get__extensionless_file(self):
        loader = Loader(search_dirs=self.search_dirs)
        self.assertRaises(IOError, loader.get, 'extensionless')

        loader.template_extension = False
        self.assertEquals(loader.get('extensionless'), "No file extension: {{foo}}")

    def test_get__load_template__unicode_return_value(self):
        """
        Check that load_template() returns unicode strings.

        """
        loader = Loader(search_dirs=self.search_dirs)
        template = loader.get('simple')

        self.assertEqual(type(template), unicode)
