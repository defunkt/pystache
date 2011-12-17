# coding: utf-8

"""
Defines a Context class to represent mustache(5)'s notion of context.

"""

# We use this private global variable as a return value to represent a key
# not being found on lookup.  This lets us distinguish between the case
# of a key's value being None with the case of a key not being found --
# without having to rely on exceptions (e.g. KeyError) for flow control.
_NOT_FOUND = object()


# TODO: share code with template.check_callable().
def _is_callable(obj):
    return hasattr(obj, '__call__')


def _get_item(obj, key):
    """
    Return a key's value, or _NOT_FOUND if the key does not exist.

    The obj argument should satisfy the same conditions as those
    described for the arguments passed to Context.__init__().  These
    conditions are described in Context.__init__()'s docstring.

    The rules for looking up the value of a key are the same as the rules
    described in Context.get()'s docstring for querying a single item.

    The behavior of this function is undefined if obj is None.

    """
    if hasattr(obj, '__getitem__'):
        # We do a membership test to avoid using exceptions for flow control
        # (e.g. catching KeyError).  In addition, we call __contains__()
        # explicitly as opposed to using the membership operator "in" to
        # avoid triggering the following Python fallback behavior:
        #
        #    "For objects that don’t define __contains__(), the membership test
        #    first tries iteration via __iter__(), then the old sequence
        #    iteration protocol via __getitem__()...."
        #
        # (from http://docs.python.org/reference/datamodel.html#object.__contains__ )
        if obj.__contains__(key):
            return obj[key]

    elif hasattr(obj, key):
        attr = getattr(obj, key)
        if _is_callable(attr):
            return attr()

        return attr

    return _NOT_FOUND


class Context(object):

    """
    Provides dictionary-like access to a stack of zero or more items.

    Instances of this class are meant to act as the rendering context
    when rendering mustache templates in accordance with mustache(5).

    Instances encapsulate a private stack of objects and dictionaries.
    Querying the stack for the value of a key queries the items in the
    stack in order from last-added objects to first (last in, first out).

    See the docstrings of the methods of this class for more information.

    """

    # We reserve keyword arguments for future options (e.g. a "strict=True"
    # option for enabling a strict mode).
    def __init__(self, *items):
        """
        Construct an instance, and initialize the private stack.

        The *items arguments are the items with which to populate the
        initial stack.  Items in the argument list are added to the
        stack in order so that, in particular, items at the end of
        the argument list are queried first when querying the stack.

        Each item should satisfy the following condition:

        * If the item implements __getitem__(), it should also implement
          __contains__().  Failure to implement __contains__() will cause
          an AttributeError to be raised when the item is queried during
          calls to self.get().

          Python dictionaries, in particular, satisfy this condition.
          An item satisfying this condition we informally call a "mapping
          object" because it shares some characteristics of the Mapping
          abstract base class (ABC) in Python's collections package:
          http://docs.python.org/library/collections.html#collections-abstract-base-classes

          It is not necessary for an item to implement __getitem__().
          In particular, an item can be an ordinary object with no
          mapping-like characteristics.

        """
        self._stack = list(items)

    def get(self, key, default=None):
        """
        Query the stack for the given key, and return the resulting value.

        Querying for a key queries items in the stack in order from last-
        added objects to first (last in, first out).  The value returned
        is the value of the key for the first item for which the item
        contains the key.  If the key is not found in any item in the
        stack, then this method returns the default value.  The default
        value defaults to None.

        Querying an item in the stack is done in the following way:

        (1) If the item defines __getitem__() and the item contains the
            key (i.e. __contains__() returns True), then the corresponding
            value is returned.
        (2) Otherwise, the method looks for an attribute with the same
            name as the key.  If such an attribute exists, the value of
            this attribute is returned.  If the attribute is callable,
            however, the attribute is first called with no arguments.
        (3) If there is no attribute with the same name as the key, then
            the key is considered not found in the item.

        """
        for obj in reversed(self._stack):
            val = _get_item(obj, key)
            if val is _NOT_FOUND:
                continue
            # Otherwise, the key was found.
            return val
        # Otherwise, no item in the stack contained the key.

        return default

    def push(self, item):
        self._stack.append(item)

    def pop(self):
        return self._stack.pop()

