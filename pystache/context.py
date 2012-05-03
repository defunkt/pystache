# coding: utf-8

"""
Exposes a ContextStack class.

"""

# This equals '__builtin__' in Python 2 and 'builtins' in Python 3.
_BUILTIN_MODULE = type(0).__module__


# We use this private global variable as a return value to represent a key
# not being found on lookup.  This lets us distinguish between the case
# of a key's value being None with the case of a key not being found --
# without having to rely on exceptions (e.g. KeyError) for flow control.
#
# TODO: eliminate the need for a private global variable, e.g. by using the
#   preferred Python approach of "easier to ask for forgiveness than permission":
#     http://docs.python.org/glossary.html#term-eafp
class NotFound(object):
    pass
_NOT_FOUND = NotFound()


# TODO: share code with template.check_callable().
def _is_callable(obj):
    return hasattr(obj, '__call__')


# TODO: document what a "context" is as opposed to a context stack.
def _get_value(context, key):
    """
    Retrieve a key's value from a context item.

    Returns _NOT_FOUND if the key does not exist.

    The ContextStack.get() docstring documents this function's intended behavior.

    """
    if isinstance(context, dict):
        # Then we consider the argument a "hash" for the purposes of the spec.
        #
        # We do a membership test to avoid using exceptions for flow control
        # (e.g. catching KeyError).
        if key in context:
            return context[key]
    elif type(context).__module__ != _BUILTIN_MODULE:
        # Then we consider the argument an "object" for the purposes of
        # the spec.
        #
        # The elif test above lets us avoid treating instances of built-in
        # types like integers and strings as objects (cf. issue #81).
        # Instances of user-defined classes on the other hand, for example,
        # are considered objects by the test above.
        if hasattr(context, key):
            attr = getattr(context, key)
            if _is_callable(attr):
                return attr()
            return attr

    return _NOT_FOUND


class ContextStack(object):

    """
    Provides dictionary-like access to a stack of zero or more items.

    Instances of this class are meant to act as the rendering context
    when rendering Mustache templates in accordance with mustache(5)
    and the Mustache spec.

    Instances encapsulate a private stack of hashes, objects, and built-in
    type instances.  Querying the stack for the value of a key queries
    the items in the stack in order from last-added objects to first
    (last in, first out).

    Caution: this class does not currently support recursive nesting in
    that items in the stack cannot themselves be ContextStack instances.

    See the docstrings of the methods of this class for more details.

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

        Caution: items should not themselves be ContextStack instances, as
        recursive nesting does not behave as one might expect.

        """
        self._stack = list(items)

    def __repr__(self):
        """
        Return a string representation of the instance.

        For example--

        >>> context = ContextStack({'alpha': 'abc'}, {'numeric': 123})
        >>> repr(context)
        "ContextStack({'alpha': 'abc'}, {'numeric': 123})"

        """
        return "%s%s" % (self.__class__.__name__, tuple(self._stack))

    @staticmethod
    def create(*context, **kwargs):
        """
        Build a ContextStack instance from a sequence of context-like items.

        This factory-style method is more general than the ContextStack class's
        constructor in that, unlike the constructor, the argument list
        can itself contain ContextStack instances.

        Here is an example illustrating various aspects of this method:

        >>> obj1 = {'animal': 'cat', 'vegetable': 'carrot', 'mineral': 'copper'}
        >>> obj2 = ContextStack({'vegetable': 'spinach', 'mineral': 'silver'})
        >>>
        >>> context = ContextStack.create(obj1, None, obj2, mineral='gold')
        >>>
        >>> context.get('animal')
        'cat'
        >>> context.get('vegetable')
        'spinach'
        >>> context.get('mineral')
        'gold'

        Arguments:

          *context: zero or more dictionaries, ContextStack instances, or objects
            with which to populate the initial context stack.  None
            arguments will be skipped.  Items in the *context list are
            added to the stack in order so that later items in the argument
            list take precedence over earlier items.  This behavior is the
            same as the constructor's.

          **kwargs: additional key-value data to add to the context stack.
            As these arguments appear after all items in the *context list,
            in the case of key conflicts these values take precedence over
            all items in the *context list.  This behavior is the same as
            the constructor's.

        """
        items = context

        context = ContextStack()

        for item in items:
            if item is None:
                continue
            if isinstance(item, ContextStack):
                context._stack.extend(item._stack)
            else:
                context.push(item)

        if kwargs:
            context.push(kwargs)

        return context

    # TODO: add some unit tests for this.
    def get(self, name, default=u''):
        """
        Resolve a dotted name against the current context stack.

        This function follows the rules outlined in the section of the spec
        regarding tag interpolation.

        Arguments:

          name: a dotted or non-dotted name.

          default: the value to return if name resolution fails at any point.
            Defaults to the empty string since the Mustache spec says that if
            name resolution fails at any point, the result should be considered
            falsey, and should interpolate as the empty string.

        This function does not coerce the return value to a string.

        """
        if name == '.':
            # TODO: should we add a test case for an empty context stack?
            return self.top()

        parts = name.split('.')

        value = self._get_simple(parts[0])

        for part in parts[1:]:
            # TODO: consider using EAFP here instead.
            #   http://docs.python.org/glossary.html#term-eafp
            if value is _NOT_FOUND:
                break
            # The full context stack is not used to resolve the remaining parts.
            # From the spec--
            #
            #   5) If any name parts were retained in step 1, each should be
            #   resolved against a context stack containing only the result
            #   from the former resolution.  If any part fails resolution, the
            #   result should be considered falsey, and should interpolate as
            #   the empty string.
            #
            # TODO: make sure we have a test case for the above point.
            value = _get_value(value, part)

        if value is _NOT_FOUND:
            return default

        return value

    # TODO: combine the docstring for this method with the docstring for
    #   the get() method.
    def _get_simple(self, key):
        """
        Query the stack for a non-dotted key, and return the resulting value.

        Arguments:

          key: a non-dotted name.

        This method queries items in the stack in order from last-added
        objects to first (last in, first out).  The value returned is
        the value of the key in the first item that contains the key.
        If the key is not found in any item in the stack, then the default
        value is returned.  The default value defaults to None.

        When speaking about returning values from a context, the Mustache
        spec distinguishes between two types of context stack elements:
        hashes and objects.

        In accordance with the spec, this method queries items in the
        stack for a key in the following way.  For the purposes of querying,
        each item is classified into one of the following three mutually
        exclusive categories: a hash, an object, or neither:

        (1) Hash: if the item's type is a subclass of dict, then the item
            is considered a hash (in the terminology of the spec), and
            the key's value is the dictionary value of the key.  If the
            dictionary doesn't contain the key, the key is not found.

        (2) Object: if the item isn't a hash and isn't an instance of a
            built-in type, then the item is considered an object (again
            using the language of the spec).  In this case, the method
            looks for an attribute with the same name as the key.  If an
            attribute with that name exists, the value of the attribute is
            returned.  If the attribute is callable, however (i.e. if the
            attribute is a method), then the attribute is called with no
            arguments and instead that value returned.  If there is no
            attribute with the same name as the key, then the key is
            considered not found.

        (3) Neither: if the item is neither a hash nor an object, then
            the key is considered not found.

        *Caution*:

          Callables are handled differently depending on whether they are
          dictionary values, as in (1) above, or attributes, as in (2).
          The former are returned as-is, while the latter are first
          called and that value returned.

          Here is an example to illustrate:

          >>> def greet():
          ...     return "Hi Bob!"
          >>>
          >>> class Greeter(object):
          ...     greet = None
          >>>
          >>> dct = {'greet': greet}
          >>> obj = Greeter()
          >>> obj.greet = greet
          >>>
          >>> dct['greet'] is obj.greet
          True
          >>> ContextStack(dct).get('greet')  #doctest: +ELLIPSIS
          <function greet at 0x...>
          >>> ContextStack(obj).get('greet')
          'Hi Bob!'

          TODO: explain the rationale for this difference in treatment.

        """
        val = _NOT_FOUND

        for item in reversed(self._stack):
            val = _get_value(item, key)
            if val is _NOT_FOUND:
                continue
            # Otherwise, the key was found.
            break

        return val

    def push(self, item):
        """
        Push an item onto the stack.

        """
        self._stack.append(item)

    def pop(self):
        """
        Pop an item off of the stack, and return it.

        """
        return self._stack.pop()

    def top(self):
        """
        Return the item last added to the stack.

        """
        return self._stack[-1]

    def copy(self):
        """
        Return a copy of this instance.

        """
        return ContextStack(*self._stack)
