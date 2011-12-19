import os
import unittest

from pystache.loader import Loader


class LoaderTestCase(unittest.TestCase):

    search_dirs = 'examples'

    def test_init(self):
        """
        Test the __init__() constructor.

        """
        loader = Loader()
        self.assertEquals(loader.search_dirs, [os.curdir])
        self.assertTrue(loader.template_encoding is None)

        loader = Loader(search_dirs=['foo'], encoding='utf-8')
        self.assertEquals(loader.search_dirs, ['foo'])
        self.assertEquals(loader.template_encoding, 'utf-8')

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

    def test_template_is_loaded(self):
        loader = Loader(search_dirs='examples')
        template = loader.load_template('simple')

        self.assertEqual(template, 'Hi {{thing}}!{{blank}}')

    def test_using_list_of_paths(self):
        loader = Loader(search_dirs=['doesnt_exist', 'examples'])
        template = loader.load_template('simple')

        self.assertEqual(template, 'Hi {{thing}}!{{blank}}')

    def test_non_existent_template_fails(self):
        loader = Loader()

        self.assertRaises(IOError, loader.load_template, 'doesnt_exist')

    def test_load_template__extensionless_file(self):
        loader = Loader(search_dirs=self.search_dirs)
        self.assertRaises(IOError, loader.load_template, 'extensionless')

        loader.template_extension = False
        self.assertEquals(loader.load_template('extensionless'), "No file extension: {{foo}}")
