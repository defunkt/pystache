# coding: utf-8

"""
Defines a class responsible for rendering logic.

"""

import cgi
import collections
import inspect
import re
import types


try:
    # The collections.Callable class is not available until Python 2.6.
    import collections.Callable
    def check_callable(it):
        return isinstance(it, collections.Callable)
except ImportError:
    def check_callable(it):
        return hasattr(it, '__call__')


class Modifiers(dict):

    """Dictionary with a decorator for assigning functions to keys."""

    def set(self, key):
        """
        Return a decorator that assigns the given function to the given key.

        >>> modifiers = Modifiers()
        >>>
        >>> @modifiers.set('P')
        ... def render_tongue(tag_name, context):
        ...     return "%s :P" % context.get(tag_name)
        >>>
        >>> modifiers['P']('text', {'text': 'hello!'})
        'hello! :P'

        """
        def decorate(func):
            self[key] = func
            return func
        return decorate


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
    otag = '{{'
    ctag = '}}'

    modifiers = Modifiers()

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
        _template = Template(template=template)

        _template.to_unicode = self.literal
        _template.escape = self.escape
        _template.get_partial = self.load_partial

        return _template.render_template(template=template, context=context)

    def _compile_regexps(self):
        """
        Compile and set the regular expression attributes.

        This method uses the current values for the otag and ctag attributes.

        """
        tags = {
            'otag': re.escape(self.otag),
            'ctag': re.escape(self.ctag)
        }

        # The section contents include white space to comply with the spec's
        # requirement that sections not alter surrounding whitespace.
        section = r"%(otag)s([#|^])([^\}]*)%(ctag)s(.+?)%(otag)s/\2%(ctag)s" % tags
        self.section_re = re.compile(section, re.M|re.S)

        tag = r"%(otag)s(#|=|&|!|>|\{)?(.+?)\1?%(ctag)s+" % tags
        # We use re.DOTALL to permit multiline comments, in accordance with the spec.
        self.tag_re = re.compile(tag, re.DOTALL)

    def _render_tags(self, template):
        output = []

        while True:
            parts = self.tag_re.split(template, maxsplit=1)
            output.append(parts[0])

            if len(parts) < 2:
                # Then there was no match.
                break

            tag_type, tag_name, template = parts[1:]

            tag_name = tag_name.strip()
            func = self.modifiers[tag_type]
            tag_value = func(self, tag_name)

            # Appending the tag value to the output prevents treating the
            # value as a template string (bug: issue #44).
            output.append(tag_value)

        output = "".join(output)

        return output

    def _render_dictionary(self, template, context):
        self.context.push(context)
        out = self._render(template)
        self.context.pop()

        return out

    def _render_list(self, template, listing):
        insides = []
        for item in listing:
            insides.append(self._render_dictionary(template, item))

        return ''.join(insides)

    def _get_string_context(self, tag_name):
        """
        Get a value from the current context as a basestring instance.

        """
        val = self.context.get(tag_name)

        # We use "==" rather than "is" to compare integers, as using "is"
        # relies on an implementation detail of CPython.  The test about
        # rendering zeroes failed while using PyPy when using "is".
        # See issue #34: https://github.com/defunkt/pystache/issues/34
        if not val and val != 0:
            if tag_name != '.':
                return ''
            val = self.context.top()

        if not isinstance(val, basestring):
            val = str(val)

        return val

    @modifiers.set(None)
    def _render_escaped(self, tag_name):
        """
        Return a variable value as an escaped unicode string.

        """
        s = self._get_string_context(tag_name)
        return self.escape(s)

    @modifiers.set('{')
    @modifiers.set('&')
    def _render_literal(self, tag_name):
        """
        Return a variable value as a unicode string (unescaped).

        """
        s = self._get_string_context(tag_name)
        return self.literal(s)

    @modifiers.set('!')
    def _render_comment(self, tag_name):
        return ''

    @modifiers.set('>')
    def _render_partial(self, template_name):
        template = self.load_partial(template_name)
        return self._render(template)

    @modifiers.set('=')
    def _change_delimiter(self, tag_name):
        """
        Change the current delimiter.

        """
        self.otag, self.ctag = tag_name.split(' ')
        self._compile_regexps()

        return ''

    def _render(self, template):
        """
        Arguments:

          template: a template string with type unicode.

        """
        output = []

        while True:
            parts = self.section_re.split(template, maxsplit=1)

            start = self._render_tags(parts[0])
            output.append(start)

            if len(parts) < 2:
                # Then there was no match.
                break

            section_type, section_key, section_contents, template = parts[1:]

            section_key = section_key.strip()
            section_value = self.context.get(section_key, None)

            rendered = ''

            # Callable
            if section_value and check_callable(section_value):
                rendered = section_value(section_contents)

            # Dictionary
            elif section_value and hasattr(section_value, 'keys') and hasattr(section_value, '__getitem__'):
                if section_type != '^':
                    rendered = self._render_dictionary(section_contents, section_value)

            # Lists
            elif section_value and hasattr(section_value, '__iter__'):
                if section_type != '^':
                    rendered = self._render_list(section_contents, section_value)

            # Other objects
            elif section_value and isinstance(section_value, object):
                if section_type != '^':
                    rendered = self._render_dictionary(section_contents, section_value)

            # Falsey and Negated or Truthy and Not Negated
            elif (not section_value and section_type == '^') or (section_value and section_type != '^'):
                rendered = self._render_dictionary(section_contents, section_value)

            # Render template prior to section too
            output.append(rendered)

        output = "".join(output)
        return output

#


END_OF_LINE_CHARACTERS = ['\r', '\n']


# TODO: what are the possibilities for val?
def call(val, view, template=None):
    if callable(val):
        (args, _, _, _) = inspect.getargspec(val)

        args_count = len(args)

        if not isinstance(val, types.FunctionType):
            # Then val is an instance method.  Subtract one from the
            # argument count because Python will automatically prepend
            # self to the argument list when calling.
            args_count -=1

        if args_count is 0:
            val = val()
        elif args_count is 1 and args[0] in ['self', 'context']:
            val = val(view)
        elif args_count is 1:
            val = val(template)
        else:
            val = val(view, template)

    if callable(val):
        val = val(template)

    if val is None:
        val = ''

    return unicode(val)

def render_parse_tree(parse_tree, context, template):
    """
    Convert a parse-tree into a string.

    """
    get_string = lambda val: call(val, context, template)
    parts = map(get_string, parse_tree)
    return ''.join(parts)

def inverseTag(name, parsed, template, delims):
    def func(self):
        data = self.get(name)
        if data:
            return ''
        return render_parse_tree(parsed, self, delims)
    return func

class EndOfSection(Exception):
    def __init__(self, parse_tree, template, position):
        self.parse_tree = parse_tree
        self.template = template
        self.position = position

class Template(object):
    tag_re = None
    otag, ctag = '{{', '}}'

    def __init__(self, template=None):
        self.template = template

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

    def to_unicode(self, text):
        return unicode(text)

    def escape(self, text):
        return cgi.escape(text, True)

    def get_partial(self, name):
        pass

    def _render_partial(self, name, context):
        template = self.get_partial(name)
        return self.render_template(template, context)

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
            val = self.render_template(template, context)

        if not isinstance(val, basestring):
            val = str(val)

        return val

    def escape_tag_function(self, name):
        get_literal = self.literal_tag_function(name)
        def func(context):
            s = self._get_string_value(context, name)
            s = self.escape(s)
            return s
        return func

    def literal_tag_function(self, name):
        def func(context):
            s = self._get_string_value(context, name)
            s = self.to_unicode(s)
            return s

        return func

    def partial_tag_function(self, name, indentation=''):
        def func(context):
            nonblank = re.compile(r'^(.)', re.M)
            template = re.sub(nonblank, indentation + r'\1', self._render_partial(name, context))
            return self.render_template(template, context)
        return func

    def section_tag_function(self, name, parse_tree_, template_, delims):
        def func(context):
            template = template_
            parse_tree = parse_tree_
            data = context.get(name)
            if not data:
                data = []
            elif callable(data):
                # TODO: should we check the arity?
                template = data(template)
                parse_tree = self.parse_string_to_tree(template, delims)
                data = [ data ]
            elif type(data) not in [list, tuple]:
                data = [ data ]

            parts = []
            for element in data:
                context.push(element)
                parts.append(render_parse_tree(parse_tree, context, delims))
                context.pop()

            return ''.join(parts)
        return func

    def parse_string_to_tree(self, template, delims=('{{', '}}')):

        template = Template(template)

        template.otag = delims[0]
        template.ctag = delims[1]

        template.escape = self.escape
        template.get_partial = self.get_partial
        template.to_unicode = self.to_unicode

        template._compile_regexps()

        return template.parse_to_tree()

    def parse_to_tree(self, index=0):
        """
        Parse a template into a syntax tree.

        """
        parse_tree = []
        template = self.template
        start_index = index

        while True:
            match = self.tag_re.search(template, index)

            if match is None:
                break

            captures = match.groupdict()
            match_index = match.end('content')
            end_index = match.end()

            index = self._handle_match(parse_tree, captures, start_index, match_index, end_index)

        # Save the rest of the template.
        parse_tree.append(template[index:])

        return parse_tree

    def _handle_match(self, parse_tree, captures, start_index, match_index, end_index):
        template = self.template

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
            func = self.partial_tag_function(name, captures['whitespace'])
        elif captures['tag'] in ['#', '^']:

            try:
                self.parse_to_tree(index=end_index)
            except EndOfSection as e:
                bufr = e.parse_tree
                tmpl = e.template
                end_index = e.position

            tag = self.section_tag_function if captures['tag'] == '#' else inverseTag
            func = tag(name, bufr, tmpl, (self.otag, self.ctag))

        elif captures['tag'] in ['{', '&']:

            func = self.literal_tag_function(name)

        elif captures['tag'] == '':

            func = self.escape_tag_function(name)

        elif captures['tag'] == '/':

            # TODO: don't use exceptions for flow control.
            raise EndOfSection(parse_tree, template[start_index:match_index], end_index)

        else:
            raise Exception("'%s' is an unrecognized type!" % captures['tag'])

        parse_tree.append(func)

        return end_index

    def render_template(self, template, context, delims=('{{', '}}')):
        """
        Arguments:

          template: template string
          context: a Context instance

        """
        if not isinstance(template, basestring):
            raise AssertionError("template: %s" % repr(template))

        parse_tree = self.parse_string_to_tree(template=template, delims=delims)
        return render_parse_tree(parse_tree, context, template)

