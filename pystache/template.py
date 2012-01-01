import re
import cgi
import inspect
import types


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

def parse_to_tree(template, view, delims=('{{', '}}')):
    template = Template(template)
    template.view = view
    template.otag, template.ctag = delims
    template._compile_regexps()
    return template.parse_to_tree()

def render_parse_tree(parse_tree, view, template):
    """
    Convert a parse-tree into a string.

    """
    get_string = lambda val: call(val, view, template)
    parts = map(get_string, parse_tree)

    return ''.join(parts)

def render(template, view, delims=('{{', '}}')):
    """
    Arguments:

      template: template string
      view: context

    """
    parse_tree = parse_to_tree(template, view, delims)
    return render_parse_tree(parse_tree, view, template)

## The possible function parse-tree elements:

def partialTag(name, indentation=''):
    def func(self):
        nonblank = re.compile(r'^(.)', re.M)
        template = re.sub(nonblank, indentation + r'\1', self.partial(name))
        return render(template, self)
    return func

def sectionTag(name, parse_tree_, template_, delims):
    def func(self):
        template = template_
        parse_tree = parse_tree_
        data = self.get(name)
        if not data:
            return ''
        elif callable(data):
            template = call(val=data, view=self, template=template)
            parse_tree = parse_to_tree(template, self, delims)
            data = [ data ]
        elif type(data) not in [list, tuple]:
            data = [ data ]

        parts = []
        for element in data:
            self.context_list.insert(0, element)
            parts.append(render_parse_tree(parse_tree, self, delims))
            del self.context_list[0]

        return ''.join(parts)
    return func

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

    def __init__(self, template=None, context={}, **kwargs):
        from view import View

        self.template = template

        if kwargs:
            context.update(kwargs)

        self.view = context if isinstance(context, View) else View(context=context)
        self._compile_regexps()

    def _compile_regexps(self):
        tags = {'otag': re.escape(self.otag), 'ctag': re.escape(self.ctag)}
        tag = r"""
            (?P<content>[\s\S]*?)
            (?P<whitespace>[\ \t]*)
            %(otag)s \s*
            (?:
              (?P<change>=) \s* (?P<delims>.+?)   \s* = |
              (?P<raw>{)    \s* (?P<raw_name>.+?) \s* } |
              (?P<tag>\W?)  \s* (?P<name>[\s\S]+?)
            )
            \s* %(ctag)s
        """
        self.tag_re = re.compile(tag % tags, re.M | re.X)

    def to_unicode(self, text):
        return unicode(text)

    def escape(self, text):
        return cgi.escape(text, True)

    def escape_tag_function(self, name):
        fetch = self.literal_tag_function(name)
        def func(context):
            return self.escape(fetch(context))
        return func

    def literal_tag_function(self, name):
        def func(context):
            val = context.get(name)
            template = call(val=val, view=context)
            return self.to_unicode(render(template, context))
        return func

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
            func = partialTag(name, captures['whitespace'])
        elif captures['tag'] in ['#', '^']:

            try:
                self.parse_to_tree(index=end_index)
            except EndOfSection as e:
                bufr = e.parse_tree
                tmpl = e.template
                end_index = e.position

            tag = sectionTag if captures['tag'] == '#' else inverseTag
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

    def render(self, encoding=None):
        result = render(self.template, self.view)
        if encoding is not None:
            result = result.encode(encoding)

        return result
