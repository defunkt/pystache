# coding: utf-8

"""
Defines a Context class to represent mustache(5)'s notion of context.

"""


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
            try:
                return obj[key]
            except KeyError:
                pass

        return default


