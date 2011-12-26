# encoding: utf-8

"""
Unit tests of reader.py.

"""

import os
import sys
import unittest

from pystache.reader import Reader


DATA_DIR = 'tests/data'


class ReaderTestCase(unittest.TestCase):

    def _get_path(self, filename):
        return os.path.join(DATA_DIR, filename)

    def test_init__decode_errors(self):
        # Test the default value.
        reader = Reader()
        self.assertEquals(reader.decode_errors, 'strict')

        reader = Reader(decode_errors='replace')
        self.assertEquals(reader.decode_errors, 'replace')

    def test_init__encoding(self):
        # Test the default value.
        reader = Reader()
        self.assertEquals(reader.encoding, sys.getdefaultencoding())

        reader = Reader(encoding='foo')
        self.assertEquals(reader.encoding, 'foo')

    def test_read(self):
        """
        Test read().

        """
        reader = Reader()
        path = self._get_path('ascii.mustache')
        self.assertEquals(reader.read(path), 'ascii: abc')

    def test_read__returns_unicode(self):
        """
        Test that read() returns unicode strings.

        """
        reader = Reader()
        path = self._get_path('ascii.mustache')
        contents = reader.read(path)
        self.assertEqual(type(contents), unicode)

    def test_read__encoding(self):
        """
        Test read(): encoding attribute respected.

        """
        reader = Reader()
        path = self._get_path('nonascii.mustache')

        self.assertRaises(UnicodeDecodeError, reader.read, path)
        reader.encoding = 'utf-8'
        self.assertEquals(reader.read(path), u'non-ascii: é')

    def test_get__decode_errors(self):
        """
        Test get(): decode_errors attribute.

        """
        reader = Reader()
        path = self._get_path('nonascii.mustache')

        self.assertRaises(UnicodeDecodeError, reader.read, path)
        reader.decode_errors = 'replace'
        self.assertEquals(reader.read(path), u'non-ascii: \ufffd\ufffd')

