import unittest

from pystache.loader import Loader


class LoaderTestCase(unittest.TestCase):

    def test_init(self):
        """
        Test the __init__() constructor.

        """
        loader = Loader()
        self.assertTrue(loader.search_dirs is None)
        self.assertTrue(loader.template_encoding is None)
        self.assertEquals(loader.template_extension, 'mustache')

        loader = Loader(search_dirs=['foo'], template_encoding='utf-8', template_extension='txt')
        self.assertEquals(loader.search_dirs, ['foo'])
        self.assertEquals(loader.template_encoding, 'utf-8')
        self.assertEquals(loader.template_extension, 'txt')

    def test_template_is_loaded(self):
        loader = Loader()
        template = loader.load_template('simple', 'examples')

        self.assertEqual(template, 'Hi {{thing}}!{{blank}}')

    def test_using_list_of_paths(self):
        loader = Loader()
        template = loader.load_template('simple', ['doesnt_exist', 'examples'])

        self.assertEqual(template, 'Hi {{thing}}!{{blank}}')

    def test_non_existent_template_fails(self):
        loader = Loader()

        self.assertRaises(IOError, loader.load_template, 'simple', 'doesnt_exist')
