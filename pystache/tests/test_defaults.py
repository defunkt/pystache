import unittest

import pystache
import pystache.defaults

from pystache.tests.common import AssertStringMixin


class TestDefaults(unittest.TestCase, AssertStringMixin):
    """Set of tests to ensure that the user can override defaults."""

    def setUp(self):
        """save all the defaults."""
        defaults = [
            'DECODE_ERRORS', 'DELIMITERS',
            'FILE_ENCODING', 'MISSING_TAGS', 
            'SEARCH_DIRS', 'STRING_ENCODING',
            'TAG_ESCAPE', 'TEMPLATE_EXTENSION'
        ]
        self.saved = {}
        for e in defaults:
            self.saved[e] = getattr(pystache.defaults, e)

    def tearDown(self):
        for key, value in self.saved.items():
            setattr(pystache.defaults, key, value)

    def test_tag_escape(self):
        """Test that TAG_ESCAPE default takes effect."""
        template = u"{{foo}}"
        context = {'foo': '<'}
        actual = pystache.render(template, context)
        self.assertString(actual, u"&lt;")

        pystache.defaults.TAG_ESCAPE = lambda u: u
        actual = pystache.render(template, context)
        self.assertString(actual, u"<")

    def test_delimiters(self):
        """Test that DELIMITERS default takes effect."""
        template = u"[[foo]]{{foo}}"
        context = {'foo': 'FOO'}
        actual = pystache.render(template, context)
        self.assertString(actual, u"[[foo]]FOO")

        pystache.defaults.DELIMITERS = ('[[', ']]')
        actual = pystache.render(template, context)
        self.assertString(actual, u"FOO{{foo}}")

    def test_missing_tags(self):
        """Test that MISSING_TAGS default take effect."""
        template = u"{{foo}}"
        context = {}
        actual = pystache.render(template, context)
        self.assertString(actual, u"")

        pystache.defaults.MISSING_TAGS = 'strict'

        self.assertRaises(pystache.context.KeyNotFoundError,
                          pystache.render, template, context)
