# coding: utf-8

"""
Defines a class responsible for rendering logic.

"""

import re

from parser import Parser


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
            template string of type unicode (not a subclass).

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
            incoming strings of type markupssafe.Markup differently
            from plain unicode strings.

        """
        self.escape = escape
        self.literal = literal
        self.load_partial = load_partial

    def _get_string_value(self, context, tag_name):
        """
        Get a value from the given context as a basestring instance.

        """
        val = context.get(tag_name)

        # We use "==" rather than "is" to compare integers, as using "is"
        # relies on an implementation detail of CPython.  The test about
        # rendering zeroes failed while using PyPy when using "is".
        # See issue #34: https://github.com/defunkt/pystache/issues/34
        if not val and val != 0:
            if tag_name != '.':
                return ''
            val = context.top()

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
            return self._render(template, context)

        return get_partial

    def _make_get_inverse(self, name, parsed_template):
        def get_inverse(context):
            """
            Returns a string with type unicode.

            """
            data = context.get(name)
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
            if not data:
                data = []
            elif callable(data):
                # TODO: should we check the arity?
                template = data(template)
                parsed_template = self._parse(template, delimiters=delims)
                data = [ data ]
            elif not hasattr(data, '__iter__') or isinstance(data, dict):
                data = [ data ]

            parts = []
            for element in data:
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
          context: a Context instance.

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

          context: a Context instance.

        """
        # Be strict but not too strict.  In other words, accept str instead
        # of unicode, but don't assume anything about the encoding (e.g.
        # don't use self.literal).
        template = unicode(template)

        return self._render(template, context)
