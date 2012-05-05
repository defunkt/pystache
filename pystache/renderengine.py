# coding: utf-8

"""
Defines a class responsible for rendering logic.

"""

import re

from pystache.common import is_string
from pystache.parser import Parser


NON_BLANK_RE = re.compile(ur'^(.)', re.M)


def context_get(stack, name):
    """
    Find and return a name from a ContextStack instance.

    """
    return stack.get(name)


class RenderEngine(object):

    """
    Provides a render() method.

    This class is meant only for internal use.

    As a rule, the code in this class operates on unicode strings where
    possible rather than, say, strings of type str or markupsafe.Markup.
    This means that strings obtained from "external" sources like partials
    and variable tag values are immediately converted to unicode (or
    escaped and converted to unicode) before being operated on further.
    This makes maintaining, reasoning about, and testing the correctness
    of the code much simpler.  In particular, it keeps the implementation
    of this class independent of the API details of one (or possibly more)
    unicode subclasses (e.g. markupsafe.Markup).

    """

    def __init__(self, literal=None, escape=None, resolve_context=None,
                 resolve_partial=None):
        """
        Arguments:

          literal: the function used to convert unescaped variable tag
            values to unicode, e.g. the value corresponding to a tag
            "{{{name}}}".  The function should accept a string of type
            str or unicode (or a subclass) and return a string of type
            unicode (but not a proper subclass of unicode).
                This class will only pass basestring instances to this
            function.  For example, it will call str() on integer variable
            values prior to passing them to this function.

          escape: the function used to escape and convert variable tag
            values to unicode, e.g. the value corresponding to a tag
            "{{name}}".  The function should obey the same properties
            described above for the "literal" function argument.
                This function should take care to convert any str
            arguments to unicode just as the literal function should, as
            this class will not pass tag values to literal prior to passing
            them to this function.  This allows for more flexibility,
            for example using a custom escape function that handles
            incoming strings of type markupsafe.Markup differently
            from plain unicode strings.

          resolve_context: the function to call to resolve a name against
            a context stack.  The function should accept two positional
            arguments: a ContextStack instance and a name to resolve.

          resolve_partial: the function to call when loading a partial.
            The function should accept a template name string and return a
            template string of type unicode (not a subclass).

        """
        self.escape = escape
        self.literal = literal
        self.resolve_context = resolve_context
        self.resolve_partial = resolve_partial

    # TODO: Rename context to stack throughout this module.

    # From the spec:
    #
    #   When used as the data value for an Interpolation tag, the lambda
    #   MUST be treatable as an arity 0 function, and invoked as such.
    #   The returned value MUST be rendered against the default delimiters,
    #   then interpolated in place of the lambda.
    #
    def _get_string_value(self, context, tag_name):
        """
        Get a value from the given context as a basestring instance.

        """
        val = self.resolve_context(context, tag_name)

        if callable(val):
            # Return because _render_value() is already a string.
            return self._render_value(val(), context)

        if not is_string(val):
            return str(val)

        return val

    def _make_get_literal(self, name):
        def get_literal(context):
            """
            Returns: a string of type unicode.

            """
            s = self._get_string_value(context, name)
            return self.literal(s)

        return get_literal

    def _make_get_escaped(self, name):
        get_literal = self._make_get_literal(name)

        def get_escaped(context):
            """
            Returns: a string of type unicode.

            """
            s = self._get_string_value(context, name)
            return self.escape(s)

        return get_escaped

    def _make_get_partial(self, tag_key, leading_whitespace):

        template = self.resolve_partial(tag_key)
        # Indent before rendering.
        template = re.sub(NON_BLANK_RE, leading_whitespace + ur'\1', template)

        def get_partial(context):
            """
            Returns: a string of type unicode.

            """
            # TODO: can we do the parsing before calling this function?
            return self.render(template, context)

        return get_partial

    def _make_get_inverse(self, name, parsed_template):
        def get_inverse(context):
            """
            Returns a string with type unicode.

            """
            # TODO: is there a bug because we are not using the same
            #   logic as in _get_string_value()?
            data = self.resolve_context(context, name)
            # Per the spec, lambdas in inverted sections are considered truthy.
            if data:
                return u''
            return parsed_template.render(context)

        return get_inverse

    # TODO: the template_ and parsed_template_ arguments don't both seem
    # to be necessary.  Can we remove one of them?  For example, if
    # callable(data) is True, then the initial parsed_template isn't used.
    def _make_get_section(self, name, parsed_template, delims,
                          template, section_start_index, section_end_index):
        def get_section_value(context):
            """
            Returns: a string of type unicode.

            """
            data = self.resolve_context(context, name)

            # From the spec:
            #
            #   If the data is not of a list type, it is coerced into a list
            #   as follows: if the data is truthy (e.g. `!!data == true`),
            #   use a single-element list containing the data, otherwise use
            #   an empty list.
            #
            if not data:
                data = []
            else:
                # The least brittle way to determine whether something
                # supports iteration is by trying to call iter() on it:
                #
                #   http://docs.python.org/library/functions.html#iter
                #
                # It is not sufficient, for example, to check whether the item
                # implements __iter__ () (the iteration protocol).  There is
                # also __getitem__() (the sequence protocol).  In Python 2,
                # strings do not implement __iter__(), but in Python 3 they do.
                try:
                    iter(data)
                except TypeError:
                    # Then the value does not support iteration.
                    data = [data]
                else:
                    if is_string(data) or isinstance(data, dict):
                        # Do not treat strings and dicts (which are iterable) as lists.
                        data = [data]
                    # Otherwise, treat the value as a list.

            parts = []
            for val in data:
                if callable(val):
                    # Lambdas special case section rendering and bypass pushing
                    # the data value onto the context stack.  From the spec--
                    #
                    #   When used as the data value for a Section tag, the
                    #   lambda MUST be treatable as an arity 1 function, and
                    #   invoked as such (passing a String containing the
                    #   unprocessed section contents).  The returned value
                    #   MUST be rendered against the current delimiters, then
                    #   interpolated in place of the section.
                    #
                    #  Also see--
                    #
                    #   https://github.com/defunkt/pystache/issues/113
                    #
                    # TODO: should we check the arity?
                    val = val(template[section_start_index:section_end_index])
                    val = self._render_value(val, context, delimiters=delims)
                    parts.append(val)
                    continue

                context.push(val)
                parts.append(parsed_template.render(context))
                context.pop()

            return unicode(''.join(parts))

        return get_section_value

    def _render_value(self, val, context, delimiters=None):
        """
        Render an arbitrary value.

        """
        if not is_string(val):
            # In case the template is an integer, for example.
            val = str(val)
        if type(val) is not unicode:
            val = self.literal(val)
        return self.render(val, context, delimiters)

    def render(self, template, context_stack, delimiters=None):
        """
        Render a unicode template string, and return as unicode.

        Arguments:

          template: a template string of type unicode (but not a proper
            subclass of unicode).

          context_stack: a ContextStack instance.

        """
        parser = Parser(self, delimiters=delimiters)
        parsed_template = parser.parse(template)

        return parsed_template.render(context_stack)
