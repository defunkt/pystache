# encoding: utf-8

"""
Unit tests of reader.py.

"""

import os
import sys
import unittest

from .common import AssertStringMixin
# TODO: remove this alias.
from pystache.loader import Loader as Reader


DATA_DIR = 'tests/data'


class ReaderTestCase(unittest.TestCase, AssertStringMixin):

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

    def test_init__extension(self):
        # Test the default value.
        reader = Reader()
        self.assertEquals(reader.extension, 'mustache')

        reader = Reader(extension='foo')
        self.assertEquals(reader.extension, 'foo')

    def test_unicode__basic__input_str(self):
        """
        Test unicode(): default arguments with str input.

        """
        reader = Reader()
        actual = reader.unicode("foo")

        self.assertString(actual, u"foo")

    def test_unicode__basic__input_unicode(self):
        """
        Test unicode(): default arguments with unicode input.

        """
        reader = Reader()
        actual = reader.unicode(u"foo")

        self.assertString(actual, u"foo")

    def test_unicode__basic__input_unicode_subclass(self):
        """
        Test unicode(): default arguments with unicode-subclass input.

        """
        class UnicodeSubclass(unicode):
            pass

        s = UnicodeSubclass(u"foo")

        reader = Reader()
        actual = reader.unicode(s)

        self.assertString(actual, u"foo")

    def test_unicode__encoding_attribute(self):
        """
        Test unicode(): encoding attribute.

        """
        reader = Reader()

        non_ascii = u'é'.encode('utf-8')

        self.assertRaises(UnicodeDecodeError, reader.unicode, non_ascii)

        reader.encoding = 'utf-8'
        self.assertEquals(reader.unicode(non_ascii), u"é")

    def test_unicode__encoding_argument(self):
        """
        Test unicode(): encoding argument.

        """
        reader = Reader()

        non_ascii = u'é'.encode('utf-8')

        self.assertRaises(UnicodeDecodeError, reader.unicode, non_ascii)

        self.assertEquals(reader.unicode(non_ascii, encoding='utf-8'), u'é')

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

    def test_read__encoding__attribute(self):
        """
        Test read(): encoding attribute respected.

        """
        reader = Reader()
        path = self._get_path('non_ascii.mustache')

        self.assertRaises(UnicodeDecodeError, reader.read, path)
        reader.encoding = 'utf-8'
        self.assertEquals(reader.read(path), u'non-ascii: é')

    def test_read__encoding__argument(self):
        """
        Test read(): encoding argument respected.

        """
        reader = Reader()
        path = self._get_path('non_ascii.mustache')

        self.assertRaises(UnicodeDecodeError, reader.read, path)
        self.assertEquals(reader.read(path, encoding='utf-8'), u'non-ascii: é')

    def test_get__decode_errors(self):
        """
        Test get(): decode_errors attribute.

        """
        reader = Reader()
        path = self._get_path('non_ascii.mustache')

        self.assertRaises(UnicodeDecodeError, reader.read, path)
        reader.decode_errors = 'replace'
        self.assertEquals(reader.read(path), u'non-ascii: \ufffd\ufffd')

