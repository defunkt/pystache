# coding: utf-8

"""
Defines a Context class to represent mustache(5)'s notion of context.

"""

# We use this private global variable as a return value to represent a key
# not being found on lookup.  This lets us distinguish the case of a key's
# value being None with the case of a key not being found -- without having
# to rely on exceptions (e.g. KeyError) for flow control.
_NOT_FOUND = object()


# TODO: share code with template.check_callable().
def _is_callable(obj):
    return hasattr(obj, '__call__')


def _get_item(obj, key):
    """
    Look up the given key in the given object, and return the value.

    The obj argument should satisfy the same conditions as those described
    in Context.__init__'s() docstring.  The behavior of this method is
    undefined if obj is None.

    The rules for querying are the same as the rules described in
    Context.get()'s docstring for a single item.

    Returns _NOT_FOUND if the key is not found.

    """
    if hasattr(obj, '__getitem__'):
        # We do a membership test to avoid using exceptions for flow
        # control.  In addition, we call __contains__() explicitly as
        # opposed to using the membership operator "in" to avoid
        # triggering the following Python fallback behavior:
        #
        #    For objects that don’t define __contains__(), the membership test
        #    first tries iteration via __iter__(), then the old sequence
        #    iteration protocol via __getitem__()....
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
    Encapsulates a queryable stack of zero or more dictionary-like objects.

    Instances of this class are intended to act as the context when
    rendering mustache templates in accordance with mustache(5).

    """

    # We reserve keyword arguments for future options (e.g. a "strict=True"
    # option for enabling a strict mode).
    def __init__(self, *obj):
        """
        Construct an instance and initialize the stack.

        The variable argument list *obj are the objects with which to
        populate the initial stack.  Objects in the argument list are added
        to the stack in order so that, in particular, items at the end of
        the argument list are queried first when querying the stack.

        The objects should be dictionary-like in the following sense:

        (1) They can be dictionaries or objects.
        (2) If they implement __getitem__, a KeyError should be raised
            if __getitem__ is called on a missing key.

        For efficiency, objects should implement __contains__() for more
        efficient membership testing.  From the Python documentation--

            For objects that don’t define __contains__(), the membership test
            first tries iteration via __iter__(), then the old sequence
            iteration protocol via __getitem__()....

        (from http://docs.python.org/reference/datamodel.html#object.__contains__ )

        Failing to implement __contains__() will cause undefined behavior.
        on any key for which __getitem__() raises an exception [TODO:
        also need to take __iter__() into account]....

        """
        self.stack = list(obj)

    def get(self, key, default=None):
        """
        Query the stack for the given key, and return the resulting value.

        Querying for a key queries objects in the stack in order from
        last-added objects to first (last in, first out).

        Querying an item in the stack is done as follows:

        (1) The __getitem__ method is attempted first, if it exists.

        This method returns None if no item in the stack contains the key.

        """
        for obj in reversed(self.stack):
            val = _get_item(obj, key)
            if val is _NOT_FOUND:
                continue
            # Otherwise, the key was found.
            return val
        # Otherwise, no item in the stack contained the key.

        return default


