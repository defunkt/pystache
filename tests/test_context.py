# coding: utf-8

"""
Unit tests of context.py.

"""

import unittest

from pystache.context import Context


class ContextTestCase(unittest.TestCase):

    """
    Test the Context class.

    """

    def test_init__no_elements(self):
        """
        Check that passing nothing to __init__() raises no exception.

        """
        context = Context()

    def test_init__no_elements(self):
        """
        Check that passing more than two items to __init__() raises no exception.

        """
        context = Context({}, {}, {})

    def test_get__missing_key(self):
        """
        Test getting a missing key.

        """
        context = Context()
        self.assertTrue(context.get("foo") is None)

    def test_get__default(self):
        """
        Test that get() respects the default value .

        """
        context = Context()
        self.assertEquals(context.get("foo", "bar"), "bar")

    def test_get__key_present(self):
        """
        Test get() with a key that is present.

        """
        context = Context({"foo": "bar"})
        self.assertEquals(context.get("foo"), "bar")

    def test_get__precedence(self):
        """
        Test that get() respects the order of precedence (later items first).

        """
        context = Context({"foo": "bar"}, {"foo": "buzz"})
        self.assertEquals(context.get("foo"), "buzz")

    def test_get__fallback(self):
        """
        Check that first-added stack items are queried on context misses.

        """
        context = Context({"fuzz": "buzz"}, {"foo": "bar"})
        self.assertEquals(context.get("fuzz"), "buzz")

