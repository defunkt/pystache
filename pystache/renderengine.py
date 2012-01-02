# coding: utf-8

"""
Defines a class responsible for rendering logic.

"""

import cgi
import collections
import inspect
import re
import types


DEFAULT_TAG_OPENING = '{{'
DEFAULT_TAG_CLOSING = '}}'
END_OF_LINE_CHARACTERS = ['\r', '\n']


def render_parse_tree(parse_tree, context):
    """
    Returns: a string of type unicode.

    The elements of parse_tree can be any of the following:

     * a unicode string
     * the return value of a call to any of the following:

        * RenderEngine._make_get_literal():
            Args: context
            Returns: unicode
        * RenderEngine._make_get_escaped():
            Args: context
            Returns: unicode
        * RenderEngine._make_get_partial()
            Args: context
            Returns: unicode
        * RenderEngine._make_get_section()
            Args: context
            Returns: unicode
        * _make_get_inverse()
            Args: context
            Returns: unicode

    """
    get_unicode = lambda val: val(context) if callable(val) else val
    parts = map(get_unicode, parse_tree)
    s = ''.join(parts)

    return unicode(s)


def _make_get_inverse(name, parsed):
    def get_inverse(context):
        """
        Returns a string with type unicode.

        """
        data = context.get(name)
        if data:
            return u''
        return render_parse_tree(parsed, context)

    return get_inverse


class EndOfSection(Exception):
    def __init__(self, parse_tree, template, position):
        self.parse_tree = parse_tree
        self.template = template
        self.position = position


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

    tag_re = None

    otag = DEFAULT_TAG_OPENING
    ctag = DEFAULT_TAG_CLOSING

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

        return self._render_template(template=template, context=context)

    def _render_template(self, template, context):
        """
        Returns: a string of type unicode.

        Arguments:

          template: template string
          context: a Context instance

        """
        if type(template) is not unicode:
            raise Exception("Argument 'template' not unicode: %s: %s" % (type(template), repr(template)))

        parse_tree = self.parse_string_to_tree(template_string=template)
        return render_parse_tree(parse_tree, context)

    def parse_string_to_tree(self, template_string, delims=None):

        engine = RenderEngine(load_partial=self.load_partial,
                              literal=self.literal,
                              escape=self.escape)

        if delims is not None:
            engine.otag = delims[0]
            engine.ctag = delims[1]

        engine._compile_regexps()

        return engine.parse_to_tree(template=template_string)

    def _compile_regexps(self):

        # The possible tag type characters following the opening tag,
        # excluding "=" and "{".
        tag_types = "!>&/#^"

        # TODO: are we following this in the spec?
        #
        #   The tag's content MUST be a non-whitespace character sequence
        #   NOT containing the current closing delimiter.
        #
        tag = r"""
            (?P<content>[\s\S]*?)
            (?P<whitespace>[\ \t]*)
            %(otag)s \s*
            (?:
              (?P<change>=) \s* (?P<delims>.+?)   \s* = |
              (?P<raw>{)    \s* (?P<raw_name>.+?) \s* } |
              (?P<tag>[%(tag_types)s]?)  \s* (?P<name>[\s\S]+?)
            )
            \s* %(ctag)s
        """ % {'tag_types': tag_types, 'otag': re.escape(self.otag), 'ctag': re.escape(self.ctag)}

        self.tag_re = re.compile(tag, re.M | re.X)

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
            val = self._render_template(template, context)

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

    def _make_get_partial(self, name, indentation=''):
        def get_partial(context):
            """
            Returns: a string of type unicode.

            """
            nonblank = re.compile(r'^(.)', re.M)
            template = self.load_partial(name)
            # Indent before rendering.
            template = re.sub(nonblank, indentation + r'\1', template)
            return self._render_template(template, context)

        return get_partial

    def _make_get_section(self, name, parse_tree_, template_, delims):
        def get_section(context):
            """
            Returns: a string of type unicode.

            """
            template = template_
            parse_tree = parse_tree_
            data = context.get(name)
            if not data:
                data = []
            elif callable(data):
                # TODO: should we check the arity?
                template = data(template)
                parse_tree = self.parse_string_to_tree(template_string=template, delims=delims)
                data = [ data ]
            elif type(data) not in [list, tuple]:
                data = [ data ]

            parts = []
            for element in data:
                context.push(element)
                parts.append(render_parse_tree(parse_tree, context))
                context.pop()

            return unicode(''.join(parts))

        return get_section

    def parse_to_tree(self, template, index=0):
        """
        Parse a template into a syntax tree.

        """
        parse_tree = []
        start_index = index

        while True:
            match = self.tag_re.search(template, index)

            if match is None:
                break

            captures = match.groupdict()
            match_index = match.end('content')
            end_index = match.end()

            index = self._handle_match(template, parse_tree, captures, start_index, match_index, end_index)

        # Save the rest of the template.
        parse_tree.append(template[index:])

        return parse_tree

    def _handle_match(self, template, parse_tree, captures, start_index, match_index, end_index):

        # Normalize the captures dictionary.
        if captures['change'] is not None:
            captures.update(tag='=', name=captures['delims'])
        elif captures['raw'] is not None:
            captures.update(tag='{', name=captures['raw_name'])

        parse_tree.append(captures['content'])

        # Standalone (non-interpolation) tags consume the entire line,
        # both leading whitespace and trailing newline.
        did_tag_begin_line = match_index == 0 or template[match_index - 1] in END_OF_LINE_CHARACTERS
        did_tag_end_line = end_index == len(template) or template[end_index] in END_OF_LINE_CHARACTERS
        is_tag_interpolating = captures['tag'] in ['', '&', '{']

        if did_tag_begin_line and did_tag_end_line and not is_tag_interpolating:
            if end_index < len(template):
                end_index += template[end_index] == '\r' and 1 or 0
            if end_index < len(template):
                end_index += template[end_index] == '\n' and 1 or 0
        elif captures['whitespace']:
            parse_tree.append(captures['whitespace'])
            match_index += len(captures['whitespace'])
            captures['whitespace'] = ''

        name = captures['name']

        if captures['tag'] == '!':
            return end_index

        if captures['tag'] == '=':
            self.otag, self.ctag = name.split()
            self._compile_regexps()
            return end_index

        if captures['tag'] == '>':
            func = self._make_get_partial(name, captures['whitespace'])
        elif captures['tag'] in ['#', '^']:

            try:
                self.parse_to_tree(template=template, index=end_index)
            except EndOfSection as e:
                bufr = e.parse_tree
                tmpl = e.template
                end_index = e.position

            if captures['tag'] == '#':
                func = self._make_get_section(name, bufr, tmpl, (self.otag, self.ctag))
            else:
                func = _make_get_inverse(name, bufr)

        elif captures['tag'] in ['{', '&']:

            func = self._make_get_literal(name)

        elif captures['tag'] == '':

            func = self._make_get_escaped(name)

        elif captures['tag'] == '/':

            # TODO: don't use exceptions for flow control.
            raise EndOfSection(parse_tree, template[start_index:match_index], end_index)

        else:
            raise Exception("'%s' is an unrecognized type!" % captures['tag'])

        parse_tree.append(func)

        return end_index

