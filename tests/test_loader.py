# encoding: utf-8

import os
import sys
import unittest

from pystache.loader import Loader

DATA_DIR = 'tests/data'

class LoaderTestCase(unittest.TestCase):

    search_dirs = 'examples'

    def _loader(self):
        return Loader(search_dirs=DATA_DIR)

    def test_init__search_dirs(self):
        # Test the default value.
        loader = Loader()
        self.assertEquals(loader.search_dirs, [os.curdir])

        loader = Loader(search_dirs=['foo'])
        self.assertEquals(loader.search_dirs, ['foo'])

    def test_init__decode_errors(self):
        # Test the default value.
        loader = Loader()
        self.assertEquals(loader.decode_errors, 'strict')

        loader = Loader(decode_errors='replace')
        self.assertEquals(loader.decode_errors, 'replace')

    def test_init__encoding(self):
        # Test the default value.
        loader = Loader()
        self.assertEquals(loader.template_encoding, sys.getdefaultencoding())

        loader = Loader(encoding='foo')
        self.assertEquals(loader.template_encoding, 'foo')

    def test_init__extension(self):
        # Test the default value.
        loader = Loader()
        self.assertEquals(loader.template_extension, 'mustache')

        loader = Loader(extension='txt')
        self.assertEquals(loader.template_extension, 'txt')

        loader = Loader(extension=False)
        self.assertTrue(loader.template_extension is False)

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

    def test_get(self):
        """
        Test get().

        """
        loader = self._loader()
        self.assertEquals(loader.get('ascii'), 'ascii: abc')

    def test_get__unicode_return_value(self):
        """
        Test that get() returns unicode strings.

        """
        loader = self._loader()
        actual = loader.get('ascii')
        self.assertEqual(type(actual), unicode)

    def test_get__encoding(self):
        """
        Test get(): encoding attribute respected.

        """
        loader = self._loader()

        self.assertRaises(UnicodeDecodeError, loader.get, 'nonascii')
        loader.template_encoding = 'utf-8'
        self.assertEquals(loader.get('nonascii'), u'non-ascii: é')

    def test_get__decode_errors(self):
        """
        Test get(): decode_errors attribute.

        """
        loader = self._loader()

        self.assertRaises(UnicodeDecodeError, loader.get, 'nonascii')
        loader.decode_errors = 'replace'
        self.assertEquals(loader.get('nonascii'), u'non-ascii: \ufffd\ufffd')

