# coding: utf-8

"""
Unit tests of context.py.

"""

import unittest

from pystache.context import _NOT_FOUND
from pystache.context import _get_item
from pystache.context import Context


class AssertIsMixin:

    """A mixin for adding assertIs() to a unittest.TestCase."""

    # unittest.assertIs() is not available until Python 2.7:
    #   http://docs.python.org/library/unittest.html#unittest.TestCase.assertIsNone
    def assertIs(self, first, second):
        self.assertTrue(first is second, msg="%s is not %s" % (repr(first), repr(second)))


class SimpleObject(object):

    """A sample class that does not define __getitem__()."""

    def __init__(self):
        self.foo = "bar"

    def foo_callable(self):
        return "called..."


class MappingObject(object):

    """A sample class that implements __getitem__() and __contains__()."""

    def __init__(self):
        self._dict = {'foo': 'bar'}
        self.fuzz = 'buzz'

    def __contains__(self, key):
        return key in self._dict

    def __getitem__(self, key):
        return self._dict[key]


class GetItemTestCase(unittest.TestCase, AssertIsMixin):

    """Test context._get_item()."""

    def assertNotFound(self, obj, key):
        """
        Assert that a call to _get_item() returns _NOT_FOUND.

        """
        self.assertIs(_get_item(obj, key), _NOT_FOUND)

    ### Case: obj is a dictionary.

    def test_dictionary__key_present(self):
        """
        Test getting a key from a dictionary.

        """
        obj = {"foo": "bar"}
        self.assertEquals(_get_item(obj, "foo"), "bar")

    def test_dictionary__callable_not_called(self):
        """
        Test that callable values are returned as-is (and in particular not called).

        """
        def foo_callable(self):
            return "bar"

        obj = {"foo": foo_callable}
        self.assertNotEquals(_get_item(obj, "foo"), "bar")
        self.assertTrue(_get_item(obj, "foo") is foo_callable)

    def test_dictionary__key_missing(self):
        """
        Test getting a missing key from a dictionary.

        """
        obj = {}
        self.assertNotFound(obj, "missing")

    def test_dictionary__attributes_not_checked(self):
        """
        Test that dictionary attributes are not checked.

        """
        obj = {}
        attr_name = "keys"
        self.assertEquals(getattr(obj, attr_name)(), [])
        self.assertNotFound(obj, attr_name)

    ### Case: obj does not implement __getitem__().

    def test_object__attribute_present(self):
        """
        Test getting an attribute from an object.

        """
        obj = SimpleObject()
        self.assertEquals(_get_item(obj, "foo"), "bar")

    def test_object__attribute_missing(self):
        """
        Test getting a missing attribute from an object.

        """
        obj = SimpleObject()
        self.assertNotFound(obj, "missing")

    def test_object__attribute_is_callable(self):
        """
        Test getting a callable attribute from an object.

        """
        obj = SimpleObject()
        self.assertEquals(_get_item(obj, "foo_callable"), "called...")

    ### Case: obj implements __getitem__() (i.e. a "mapping object").

    def test_mapping__key_present(self):
        """
        Test getting a key from a mapping object.

        """
        obj = MappingObject()
        self.assertEquals(_get_item(obj, "foo"), "bar")

    def test_mapping__key_missing(self):
        """
        Test getting a missing key from a mapping object.

        """
        obj = MappingObject()
        self.assertNotFound(obj, "missing")

    def test_mapping__get_attribute(self):
        """
        Test getting an attribute from a mapping object.

        """
        obj = MappingObject()
        key = "fuzz"
        self.assertEquals(getattr(obj, key), "buzz")
        # As desired, __getitem__()'s presence causes obj.fuzz not to be checked.
        self.assertNotFound(obj, key)

    def test_mapping_object__not_implementing_contains(self):
        """
        Test querying a mapping object that doesn't define __contains__().

        """
        class Sample(object):

            def __getitem__(self, key):
                return "bar"

        obj = Sample()
        self.assertRaises(AttributeError, _get_item, obj, "foo")


class ContextTests(unittest.TestCase, AssertIsMixin):

    """
    Test the Context class.

    """

    def test_init__no_elements(self):
        """
        Check that passing nothing to __init__() raises no exception.

        """
        context = Context()

    def test_init__many_elements(self):
        """
        Check that passing more than two items to __init__() raises no exception.

        """
        context = Context({}, {}, {})

    def test__repr(self):
        context = Context()
        self.assertEquals(repr(context), 'Context()')

        context = Context({'foo': 'bar'})
        self.assertEquals(repr(context), "Context({'foo': 'bar'},)")

        context = Context({'foo': 'bar'}, {'abc': 123})
        self.assertEquals(repr(context), "Context({'foo': 'bar'}, {'abc': 123})")

    def test__str(self):
        context = Context()
        self.assertEquals(str(context), 'Context()')

        context = Context({'foo': 'bar'})
        self.assertEquals(str(context), "Context({'foo': 'bar'},)")

        context = Context({'foo': 'bar'}, {'abc': 123})
        self.assertEquals(str(context), "Context({'foo': 'bar'}, {'abc': 123})")

    ## Test the static create() method.

    def test_create__dictionary(self):
        """
        Test passing a dictionary.

        """
        context = Context.create({'foo': 'bar'})
        self.assertEquals(context.get('foo'), 'bar')

    def test_create__none(self):
        """
        Test passing None.

        """
        context = Context.create({'foo': 'bar'}, None)
        self.assertEquals(context.get('foo'), 'bar')

    def test_create__object(self):
        """
        Test passing an object.

        """
        class Foo(object):
            foo = 'bar'
        context = Context.create(Foo())
        self.assertEquals(context.get('foo'), 'bar')

    def test_create__context(self):
        """
        Test passing a Context instance.

        """
        obj = Context({'foo': 'bar'})
        context = Context.create(obj)
        self.assertEquals(context.get('foo'), 'bar')

    def test_create__kwarg(self):
        """
        Test passing a keyword argument.

        """
        context = Context.create(foo='bar')
        self.assertEquals(context.get('foo'), 'bar')

    def test_create__precedence_positional(self):
        """
        Test precedence of positional arguments.

        """
        context = Context.create({'foo': 'bar'}, {'foo': 'buzz'})
        self.assertEquals(context.get('foo'), 'buzz')

    def test_create__precedence_keyword(self):
        """
        Test precedence of keyword arguments.

        """
        context = Context.create({'foo': 'bar'}, foo='buzz')
        self.assertEquals(context.get('foo'), 'buzz')

    def test_get__key_present(self):
        """
        Test getting a key.

        """
        context = Context({"foo": "bar"})
        self.assertEquals(context.get("foo"), "bar")

    def test_get__key_missing(self):
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

    def test_push(self):
        """
        Test push().

        """
        key = "foo"
        context = Context({key: "bar"})
        self.assertEquals(context.get(key), "bar")

        context.push({key: "buzz"})
        self.assertEquals(context.get(key), "buzz")

    def test_pop(self):
        """
        Test pop().

        """
        key = "foo"
        context = Context({key: "bar"}, {key: "buzz"})
        self.assertEquals(context.get(key), "buzz")

        item = context.pop()
        self.assertEquals(item, {"foo": "buzz"})
        self.assertEquals(context.get(key), "bar")

    def test_top(self):
        key = "foo"
        context = Context({key: "bar"}, {key: "buzz"})
        self.assertEquals(context.get(key), "buzz")

        top = context.top()
        self.assertEquals(top, {"foo": "buzz"})
        # Make sure calling top() didn't remove the item from the stack.
        self.assertEquals(context.get(key), "buzz")

    def test_copy(self):
        key = "foo"
        original = Context({key: "bar"}, {key: "buzz"})
        self.assertEquals(original.get(key), "buzz")

        new = original.copy()
        # Confirm that the copy behaves the same.
        self.assertEquals(new.get(key), "buzz")
        # Change the copy, and confirm it is changed.
        new.pop()
        self.assertEquals(new.get(key), "bar")
        # Confirm the original is unchanged.
        self.assertEquals(original.get(key), "buzz")

