# encoding: utf-8

"""
Unit tests of reader.py.

"""

import os
import sys
import unittest

from pystache.tests.common import AssertStringMixin, DATA_DIR
from pystache import defaults
from pystache.loader import Loader


class LoaderTests(unittest.TestCase, AssertStringMixin):

    def test_init__extension(self):
        loader = Loader(extension='foo')
        self.assertEqual(loader.extension, 'foo')

    def test_init__extension__default(self):
        # Test the default value.
        loader = Loader()
        self.assertEqual(loader.extension, 'mustache')

    def test_init__file_encoding(self):
        loader = Loader(file_encoding='bar')
        self.assertEqual(loader.file_encoding, 'bar')

    def test_init__file_encoding__default(self):
        file_encoding = defaults.FILE_ENCODING
        try:
            defaults.FILE_ENCODING = 'foo'
            loader = Loader()
            self.assertEqual(loader.file_encoding, 'foo')
        finally:
            defaults.FILE_ENCODING = file_encoding

    def test_init__to_unicode(self):
        to_unicode = lambda x: x
        loader = Loader(to_unicode=to_unicode)
        self.assertEqual(loader.to_unicode, to_unicode)

    def test_init__to_unicode__default(self):
        loader = Loader()
        self.assertRaises(TypeError, loader.to_unicode, u"abc")

        decode_errors = defaults.DECODE_ERRORS
        string_encoding = defaults.STRING_ENCODING

        nonascii = 'abcdé'

        try:
            defaults.DECODE_ERRORS = 'strict'
            defaults.STRING_ENCODING = 'ascii'
            loader = Loader()
            self.assertRaises(UnicodeDecodeError, loader.to_unicode, nonascii)

            defaults.DECODE_ERRORS = 'ignore'
            loader = Loader()
            self.assertString(loader.to_unicode(nonascii), u'abcd')

            defaults.STRING_ENCODING = 'utf-8'
            loader = Loader()
            self.assertString(loader.to_unicode(nonascii), u'abcdé')

        finally:
            defaults.DECODE_ERRORS = decode_errors
            defaults.STRING_ENCODING = string_encoding

    def _get_path(self, filename):
        return os.path.join(DATA_DIR, filename)

    def test_unicode__basic__input_str(self):
        """
        Test unicode(): default arguments with str input.

        """
        reader = Loader()
        actual = reader.unicode("foo")

        self.assertString(actual, u"foo")

    def test_unicode__basic__input_unicode(self):
        """
        Test unicode(): default arguments with unicode input.

        """
        reader = Loader()
        actual = reader.unicode(u"foo")

        self.assertString(actual, u"foo")

    def test_unicode__basic__input_unicode_subclass(self):
        """
        Test unicode(): default arguments with unicode-subclass input.

        """
        class UnicodeSubclass(unicode):
            pass

        s = UnicodeSubclass(u"foo")

        reader = Loader()
        actual = reader.unicode(s)

        self.assertString(actual, u"foo")

    def test_unicode__to_unicode__attribute(self):
        """
        Test unicode(): encoding attribute.

        """
        reader = Loader()

        non_ascii = u'abcdé'.encode('utf-8')

        self.assertRaises(UnicodeDecodeError, reader.unicode, non_ascii)

        def to_unicode(s, encoding=None):
            if encoding is None:
                encoding = 'utf-8'
            return unicode(s, encoding)

        reader.to_unicode = to_unicode
        self.assertString(reader.unicode(non_ascii), u"abcdé")

    def test_unicode__encoding_argument(self):
        """
        Test unicode(): encoding argument.

        """
        reader = Loader()

        non_ascii = u'abcdé'.encode('utf-8')

        self.assertRaises(UnicodeDecodeError, reader.unicode, non_ascii)

        actual = reader.unicode(non_ascii, encoding='utf-8')
        self.assertString(actual, u'abcdé')

    # TODO: check the read() unit tests.
    def test_read(self):
        """
        Test read().

        """
        reader = Loader()
        path = self._get_path('ascii.mustache')
        actual = reader.read(path)
        self.assertString(actual, u'ascii: abc')

    def test_read__file_encoding__attribute(self):
        """
        Test read(): file_encoding attribute respected.

        """
        loader = Loader()
        path = self._get_path('non_ascii.mustache')

        self.assertRaises(UnicodeDecodeError, loader.read, path)

        loader.file_encoding = 'utf-8'
        actual = loader.read(path)
        self.assertString(actual, u'non-ascii: é')

    def test_read__encoding__argument(self):
        """
        Test read(): encoding argument respected.

        """
        reader = Loader()
        path = self._get_path('non_ascii.mustache')

        self.assertRaises(UnicodeDecodeError, reader.read, path)

        actual = reader.read(path, encoding='utf-8')
        self.assertString(actual, u'non-ascii: é')

    def test_reader__to_unicode__attribute(self):
        """
        Test read(): to_unicode attribute respected.

        """
        reader = Loader()
        path = self._get_path('non_ascii.mustache')

        self.assertRaises(UnicodeDecodeError, reader.read, path)

        #reader.decode_errors = 'ignore'
        #actual = reader.read(path)
        #self.assertString(actual, u'non-ascii: ')

