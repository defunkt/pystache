import re
import cgi
import inspect
import types

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

def parse(template, view, delims=('{{', '}}')):
    tmpl = Template(template)
    tmpl.view = view
    tmpl.otag, tmpl.ctag = delims
    tmpl._compile_regexps()
    return tmpl.parse_to_tree(template)

def renderParseTree(parsed, view, template):
    n = len(parsed)
    parts = map(call, parsed, [view] * n, [template] * n)
    return ''.join(parts)

def render(template, view, delims=('{{', '}}')):
    parseTree = parse(template, view, delims)
    return renderParseTree(parseTree, view, template)

def partialTag(name, indentation=''):
    def func(self):
        nonblank = re.compile(r'^(.)', re.M)
        template = re.sub(nonblank, indentation + r'\1', self.partial(name))
        return render(template, self)
    return func

def sectionTag(name, parsed, template, delims):
    def func(self):
        data = self.get(name)
        ast = parsed
        if not data:
            return ''
        elif callable(data):
            ast = parse(call(view=self, val=data, template=template), self, delims)
            data = [ data ]
        elif type(data) not in [list, tuple]:
            data = [ data ]

        parts = []
        for element in data:
            self.context_list.insert(0, element)
            parts.append(renderParseTree(ast, self, delims))
            del self.context_list[0]

        return ''.join(parts)
    return func

def inverseTag(name, parsed, template, delims):
    def func(self):
        data = self.get(name)
        if data:
            return ''
        return renderParseTree(parsed, self, delims)
    return func

def escapedTag(name, delims):
    fetch = unescapedTag(name, delims)
    def func(self):
        return cgi.escape(fetch(self), True)
    return func

def unescapedTag(name, delims):
    def func(context):
        val = context.get(name)
        template = call(val=val, view=context)
        return unicode(render(template, context))
    return func

class EndOfSection(Exception):
    def __init__(self, buffer, template, position):
        self.buffer   = buffer
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

            index = self._handle_match(template, match, parse_tree, start_index)

        # Save the rest of the template.
        parse_tree.append(template[index:])

        return parse_tree

    def _handle_match(self, template, match, buffer, start_index):
        # Normalize the captures dictionary.
        captures = match.groupdict()
        if captures['change'] is not None:
            captures.update(tag='=', name=captures['delims'])
        elif captures['raw'] is not None:
            captures.update(tag='{', name=captures['raw_name'])

        # Save the literal text content.
        buffer.append(captures['content'])
        end_index = match.end()
        tagPos = match.end('content')

        # Standalone (non-interpolation) tags consume the entire line,
        # both leading whitespace and trailing newline.
        tagBeganLine = not tagPos or template[tagPos - 1] in ['\r', '\n']
        tagEndedLine = (end_index == len(template) or template[end_index] in ['\r', '\n'])
        interpolationTag = captures['tag'] in ['', '&', '{']

        if (tagBeganLine and tagEndedLine and not interpolationTag):
            if end_index < len(template):
                end_index += template[end_index] == '\r' and 1 or 0
            if end_index < len(template):
                end_index += template[end_index] == '\n' and 1 or 0
        elif captures['whitespace']:
            buffer.append(captures['whitespace'])
            tagPos += len(captures['whitespace'])
            captures['whitespace'] = ''

        name = captures['name']
        if captures['tag'] == '!':
            pass
        elif captures['tag'] == '=':
            self.otag, self.ctag = name.split()
            self._compile_regexps()
        elif captures['tag'] == '>':
            buffer.append(partialTag(name, captures['whitespace']))
        elif captures['tag'] in ['#', '^']:
            try:
                self.parse_to_tree(template, index=end_index)
            except EndOfSection as e:
                bufr = e.buffer
                tmpl = e.template
                end_index  = e.position

            tag = { '#': sectionTag, '^': inverseTag }[captures['tag']]
            buffer.append(tag(name, bufr, tmpl, (self.otag, self.ctag)))
        elif captures['tag'] == '/':
            raise EndOfSection(buffer, template[start_index:tagPos], end_index)
        elif captures['tag'] in ['{', '&']:
            buffer.append(unescapedTag(name, (self.otag, self.ctag)))
        elif captures['tag'] == '':
            buffer.append(escapedTag(name, (self.otag, self.ctag)))
        else:
            raise Exception("'%s' is an unrecognized type!" % captures['tag'])

        return end_index

    def render(self, encoding=None):
        result = render(self.template, self.view)
        if encoding is not None:
            result = result.encode(encoding)

        return result
