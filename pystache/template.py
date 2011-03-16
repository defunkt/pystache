import re
import cgi
import inspect

def call(view, x):
    if callable(x):
        (args, _, _, _) = inspect.getargspec(x)
        if len(args) is 0:
            x = x()
        elif len(args) is 1 and args[0] == 'self':
            x = x(view)
    return unicode(x)

def sectionTag(name, parsed, template, delims):
    def func(self):
        data = self.get(name)
        if not data:
            return ''
        elif type(data) not in [list, tuple]:
            data = [ data ]

        parts = []
        for element in data:
            self.context_list.insert(0, element)
            parts.append(''.join(map(call, [self] * len(parsed), parsed)))
            del self.context_list[0]

        return ''.join(parts)
    return func

def inverseTag(name, parsed, template, delims):
    def func(self):
        data = self.get(name)
        if data:
            return ''
        return ''.join(map(call, [self] * len(parsed), parsed))
    return func

def escapedTag(name):
    fetch = unescapedTag(name)
    def func(self):
        return cgi.escape(fetch(self), True)
    return func

def unescapedTag(name):
    def func(self):
        return unicode(call(self, self.get(name)))
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

    def _parse(self, template=None, section=None, index=0):
        """Parse a template into a syntax tree."""

        template = template != None and template or self.template
        buffer = []
        pos = index

        while True:
            match = self.tag_re.search(template, pos)

            if match is None:
                break

            pos = self._handle_match(template, match, buffer, index)

        # Save the rest of the template.
        buffer.append(template[pos:])

        return buffer

    def _handle_match(self, template, match, buffer, index):
        # Normalize the captures dictionary.
        captures = match.groupdict()
        if captures['change'] is not None:
            captures.update(tag='=', name=captures['delims'])
        elif captures['raw'] is not None:
            captures.update(tag='{', name=captures['raw_name'])

        # Save the literal text content.
        buffer.append(captures['content'])
        pos = match.end()
        tagPos = match.end('content')

        # Standalone (non-interpolation) tags consume the entire line,
        # both leading whitespace and trailing newline.
        tagBeganLine = not tagPos or template[tagPos - 1] == '\n'
        tagEndedLine = (pos == len(template) or template[pos] == '\n')
        interpolationTag = captures['tag'] in ['', '&', '{']

        if (tagBeganLine and tagEndedLine and not interpolationTag):
            pos += 1
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
            buffer += self._parse(self.view.partial(name))
        elif captures['tag'] in ['#', '^']:
            try:
                self._parse(template, name, pos)
            except EndOfSection as e:
                bufr = e.buffer
                tmpl = e.template
                pos  = e.position

            tag = { '#': sectionTag, '^': inverseTag }[captures['tag']]
            buffer.append(tag(name, bufr, tmpl, (self.otag, self.ctag)))
        elif captures['tag'] == '/':
            raise EndOfSection(buffer, template[index:tagPos], pos)
        elif captures['tag'] in ['{', '&']:
            buffer.append(unescapedTag(name))
        elif captures['tag'] == '':
            buffer.append(escapedTag(name))
        else:
            raise Exception("'%s' is an unrecognized type!" % captures['tag'])

        return pos

    def render(self, encoding=None):
        parsed = self._parse()
        result = ''.join(map(call, [self.view] * len(parsed), parsed))
        if encoding is not None:
            result = result.encode(encoding)

        return result
