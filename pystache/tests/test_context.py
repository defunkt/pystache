# coding: utf-8

"""
Unit tests of context.py.

"""

from datetime import datetime
import unittest

from pystache.context import _NOT_FOUND
from pystache.context import _get_value
from pystache.context import Context
from pystache.tests.common import AssertIsMixin

class SimpleObject(object):

    """A sample class that does not define __getitem__()."""

    def __init__(self):
        self.foo = "bar"

    def foo_callable(self):
        return "called..."


class DictLike(object):

    """A sample class that implements __getitem__() and __contains__()."""

    def __init__(self):
        self._dict = {'foo': 'bar'}
        self.fuzz = 'buzz'

    def __contains__(self, key):
        return key in self._dict

    def __getitem__(self, key):
        return self._dict[key]


class GetValueTests(unittest.TestCase, AssertIsMixin):

    """Test context._get_value()."""

    def assertNotFound(self, item, key):
        """
        Assert that a call to _get_value() returns _NOT_FOUND.

        """
        self.assertIs(_get_value(item, key), _NOT_FOUND)

    ### Case: the item is a dictionary.

    def test_dictionary__key_present(self):
        """
        Test getting a key from a dictionary.

        """
        item = {"foo": "bar"}
        self.assertEqual(_get_value(item, "foo"), "bar")

    def test_dictionary__callable_not_called(self):
        """
        Test that callable values are returned as-is (and in particular not called).

        """
        def foo_callable(self):
            return "bar"

        item = {"foo": foo_callable}
        self.assertNotEqual(_get_value(item, "foo"), "bar")
        self.assertTrue(_get_value(item, "foo") is foo_callable)

    def test_dictionary__key_missing(self):
        """
        Test getting a missing key from a dictionary.

        """
        item = {}
        self.assertNotFound(item, "missing")

    def test_dictionary__attributes_not_checked(self):
        """
        Test that dictionary attributes are not checked.

        """
        item = {1: 2, 3: 4}
        # I was not able to find a "public" attribute of dict that is
        # the same across Python 2/3.
        attr_name = "__len__"
        self.assertEqual(getattr(item, attr_name)(), 2)
        self.assertNotFound(item, attr_name)

    def test_dictionary__dict_subclass(self):
        """
        Test that subclasses of dict are treated as dictionaries.

        """
        class DictSubclass(dict): pass

        item = DictSubclass()
        item["foo"] = "bar"

        self.assertEqual(_get_value(item, "foo"), "bar")

    ### Case: the item is an object.

    def test_object__attribute_present(self):
        """
        Test getting an attribute from an object.

        """
        item = SimpleObject()
        self.assertEqual(_get_value(item, "foo"), "bar")

    def test_object__attribute_missing(self):
        """
        Test getting a missing attribute from an object.

        """
        item = SimpleObject()
        self.assertNotFound(item, "missing")

    def test_object__attribute_is_callable(self):
        """
        Test getting a callable attribute from an object.

        """
        item = SimpleObject()
        self.assertEqual(_get_value(item, "foo_callable"), "called...")

    def test_object__non_built_in_type(self):
        """
        Test getting an attribute from an instance of a type that isn't built-in.

        """
        item = datetime(2012, 1, 2)
        self.assertEqual(_get_value(item, "day"), 2)

    def test_object__dict_like(self):
        """
        Test getting a key from a dict-like object (an object that implements '__getitem__').

        """
        item = DictLike()
        self.assertEqual(item["foo"], "bar")
        self.assertNotFound(item, "foo")

    ### Case: the item is an instance of a built-in type.

    def test_built_in_type__integer(self):
        """
        Test getting from an integer.

        """
        class MyInt(int): pass

        cust_int = MyInt(10)
        pure_int = 10

        # We have to use a built-in method like __neg__ because "public"
        # attributes like "real" were not added to Python until Python 2.6,
        # when the numeric type hierarchy was added:
        #
        #   http://docs.python.org/library/numbers.html
        #
        self.assertEqual(cust_int.__neg__(), -10)
        self.assertEqual(pure_int.__neg__(), -10)

        self.assertEqual(_get_value(cust_int, '__neg__'), -10)
        self.assertNotFound(pure_int, '__neg__')

    def test_built_in_type__string(self):
        """
        Test getting from a string.

        """
        class MyStr(str): pass

        item1 = MyStr('abc')
        item2 = 'abc'

        self.assertEqual(item1.upper(), 'ABC')
        self.assertEqual(item2.upper(), 'ABC')

        self.assertEqual(_get_value(item1, 'upper'), 'ABC')
        self.assertNotFound(item2, 'upper')

    def test_built_in_type__list(self):
        """
        Test getting from a list.

        """
        class MyList(list): pass

        item1 = MyList([1, 2, 3])
        item2 = [1, 2, 3]

        self.assertEqual(item1.pop(), 3)
        self.assertEqual(item2.pop(), 3)

        self.assertEqual(_get_value(item1, 'pop'), 2)
        self.assertNotFound(item2, 'pop')


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
        self.assertEqual(repr(context), 'Context()')

        context = Context({'foo': 'bar'})
        self.assertEqual(repr(context), "Context({'foo': 'bar'},)")

        context = Context({'foo': 'bar'}, {'abc': 123})
        self.assertEqual(repr(context), "Context({'foo': 'bar'}, {'abc': 123})")

    def test__str(self):
        context = Context()
        self.assertEqual(str(context), 'Context()')

        context = Context({'foo': 'bar'})
        self.assertEqual(str(context), "Context({'foo': 'bar'},)")

        context = Context({'foo': 'bar'}, {'abc': 123})
        self.assertEqual(str(context), "Context({'foo': 'bar'}, {'abc': 123})")

    ## Test the static create() method.

    def test_create__dictionary(self):
        """
        Test passing a dictionary.

        """
        context = Context.create({'foo': 'bar'})
        self.assertEqual(context.get('foo'), 'bar')

    def test_create__none(self):
        """
        Test passing None.

        """
        context = Context.create({'foo': 'bar'}, None)
        self.assertEqual(context.get('foo'), 'bar')

    def test_create__object(self):
        """
        Test passing an object.

        """
        class Foo(object):
            foo = 'bar'
        context = Context.create(Foo())
        self.assertEqual(context.get('foo'), 'bar')

    def test_create__context(self):
        """
        Test passing a Context instance.

        """
        obj = Context({'foo': 'bar'})
        context = Context.create(obj)
        self.assertEqual(context.get('foo'), 'bar')

    def test_create__kwarg(self):
        """
        Test passing a keyword argument.

        """
        context = Context.create(foo='bar')
        self.assertEqual(context.get('foo'), 'bar')

    def test_create__precedence_positional(self):
        """
        Test precedence of positional arguments.

        """
        context = Context.create({'foo': 'bar'}, {'foo': 'buzz'})
        self.assertEqual(context.get('foo'), 'buzz')

    def test_create__precedence_keyword(self):
        """
        Test precedence of keyword arguments.

        """
        context = Context.create({'foo': 'bar'}, foo='buzz')
        self.assertEqual(context.get('foo'), 'buzz')

    def test_get__key_present(self):
        """
        Test getting a key.

        """
        context = Context({"foo": "bar"})
        self.assertEqual(context.get("foo"), "bar")

    def test_get__key_missing(self):
        """
        Test getting a missing key.

        """
        context = Context()
        self.assertTrue(context.get("foo") is None)

    def test_get__default(self):
        """
        Test that get() respects the default value.

        """
        context = Context()
        self.assertEqual(context.get("foo", "bar"), "bar")

    def test_get__precedence(self):
        """
        Test that get() respects the order of precedence (later items first).

        """
        context = Context({"foo": "bar"}, {"foo": "buzz"})
        self.assertEqual(context.get("foo"), "buzz")

    def test_get__fallback(self):
        """
        Check that first-added stack items are queried on context misses.

        """
        context = Context({"fuzz": "buzz"}, {"foo": "bar"})
        self.assertEqual(context.get("fuzz"), "buzz")

    def test_push(self):
        """
        Test push().

        """
        key = "foo"
        context = Context({key: "bar"})
        self.assertEqual(context.get(key), "bar")

        context.push({key: "buzz"})
        self.assertEqual(context.get(key), "buzz")

    def test_pop(self):
        """
        Test pop().

        """
        key = "foo"
        context = Context({key: "bar"}, {key: "buzz"})
        self.assertEqual(context.get(key), "buzz")

        item = context.pop()
        self.assertEqual(item, {"foo": "buzz"})
        self.assertEqual(context.get(key), "bar")

    def test_top(self):
        key = "foo"
        context = Context({key: "bar"}, {key: "buzz"})
        self.assertEqual(context.get(key), "buzz")

        top = context.top()
        self.assertEqual(top, {"foo": "buzz"})
        # Make sure calling top() didn't remove the item from the stack.
        self.assertEqual(context.get(key), "buzz")

    def test_copy(self):
        key = "foo"
        original = Context({key: "bar"}, {key: "buzz"})
        self.assertEqual(original.get(key), "buzz")

        new = original.copy()
        # Confirm that the copy behaves the same.
        self.assertEqual(new.get(key), "buzz")
        # Change the copy, and confirm it is changed.
        new.pop()
        self.assertEqual(new.get(key), "bar")
        # Confirm the original is unchanged.
        self.assertEqual(original.get(key), "buzz")

