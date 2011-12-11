import unittest

from pystache.loader import Loader


class LoaderTestCase(unittest.TestCase):

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
