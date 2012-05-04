# coding: utf-8

"""
Defines a class responsible for rendering logic.

"""

import re

from pystache.parser import Parser


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

    def __init__(self, load_partial=None, literal=None, escape=None):
        """
        Arguments:

          load_partial: the function to call when loading a partial.  The
            function should accept a string template name and return a
            template string of type unicode (not a subclass).  If the
            template is not found, it should raise a TemplateNotFoundError.

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

        """
        self.escape = escape
        self.literal = literal
        self.load_partial = load_partial

    # TODO: rename context to stack throughout this module.
    def _get_string_value(self, context, tag_name):
        """
        Get a value from the given context as a basestring instance.

        """
        val = context.get(tag_name)

        if callable(val):
            # According to the spec:
            #
            #     When used as the data value for an Interpolation tag,
            #     the lambda MUST be treatable as an arity 0 function,
            #     and invoked as such.  The returned value MUST be
            #     rendered against the default delimiters, then
            #     interpolated in place of the lambda.
            template = val()
            if not isinstance(template, basestring):
                # In case the template is an integer, for example.
                template = str(template)
            if type(template) is not unicode:
                template = self.literal(template)
            val = self._render(template, context)

        if not isinstance(val, basestring):
            val = str(val)

        return val

    def _make_get_literal(self, name):
        def get_literal(context):
            """
            Returns: a string of type unicode.

            """
            s = self._get_string_value(context, name)
            s = self.literal(s)
            return s

        return get_literal

    def _make_get_escaped(self, name):
        get_literal = self._make_get_literal(name)

        def get_escaped(context):
            """
            Returns: a string of type unicode.

            """
            s = self._get_string_value(context, name)
            s = self.escape(s)
            return s

        return get_escaped

    def _make_get_partial(self, template):
        def get_partial(context):
            """
            Returns: a string of type unicode.

            """
            # TODO: the parsing should be done before calling this function.
            return self._render(template, context)

        return get_partial

    def _make_get_inverse(self, name, parsed_template):
        def get_inverse(context):
            """
            Returns a string with type unicode.

            """
            # TODO: is there a bug because we are not using the same
            #   logic as in _get_string_value()?
            data = context.get(name)
            # Per the spec, lambdas in inverted sections are considered truthy.
            if data:
                return u''
            return parsed_template.render(context)

        return get_inverse

    # TODO: the template_ and parsed_template_ arguments don't both seem
    # to be necessary.  Can we remove one of them?  For example, if
    # callable(data) is True, then the initial parsed_template isn't used.
    def _make_get_section(self, name, parsed_template_, template_, delims):
        def get_section(context):
            """
            Returns: a string of type unicode.

            """
            template = template_
            parsed_template = parsed_template_
            data = context.get(name)

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
                    if isinstance(data, (basestring, dict)):
                        # Do not treat strings and dicts (which are iterable) as lists.
                        data = [data]
                    # Otherwise, treat the value as a list.

            parts = []
            for element in data:
                if callable(element):
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
                    new_template = element(template)
                    new_parsed_template = self._parse(new_template, delimiters=delims)
                    parts.append(new_parsed_template.render(context))
                    continue

                context.push(element)
                parts.append(parsed_template.render(context))
                context.pop()

            return unicode(''.join(parts))

        return get_section

    def _parse(self, template, delimiters=None):
        """
        Parse the given template, and return a ParsedTemplate instance.

        Arguments:

          template: a template string of type unicode.

        """
        parser = Parser(self, delimiters=delimiters)
        parser.compile_template_re()

        return parser.parse(template=template)

    def _render(self, template, context):
        """
        Returns: a string of type unicode.

        Arguments:

          template: a template string of type unicode.
          context: a ContextStack instance.

        """
        # We keep this type-check as an added check because this method is
        # called with template strings coming from potentially externally-
        # supplied functions like self.literal, self.load_partial, etc.
        # Beyond this point, we have much better control over the type.
        if type(template) is not unicode:
            raise Exception("Argument 'template' not unicode: %s: %s" % (type(template), repr(template)))

        parsed_template = self._parse(template)

        return parsed_template.render(context)

    def render(self, template, context):
        """
        Return a template rendered as a string with type unicode.

        Arguments:

          template: a template string of type unicode (but not a proper
            subclass of unicode).

          context: a ContextStack instance.

        """
        # Be strict but not too strict.  In other words, accept str instead
        # of unicode, but don't assume anything about the encoding (e.g.
        # don't use self.literal).
        template = unicode(template)

        return self._render(template, context)
