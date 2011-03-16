import re
import cgi

def call(view):
    def _(x):
        return unicode(callable(x) and x(view) or x)
    return _

def sectionTag(name, template, delims):
    def func(view):
        if not view.get(name):
            return ''
        print template
        tmpl = Template(template)
        tmpl.view = view
        (tmpl.otag, tmpl.ctag) = delims
        view.context_list = [view.get(name)] + view.context_list
        string = ''.join(map(call(view), tmpl._parse()))
        return string
    return func

def inverseTag(name, template, delims):
    def func(view):
        if view.get(name):
            return ''
        tmpl = Template(template)
        tmpl.view = view
        (tmpl.otag, tmpl.ctag) = delims
        return ''.join(map(call(view), tmpl._parse()))
    return func

def escapedTag(name):
    def func(view):
        return cgi.escape(unicode(view.get(name)), True)
    return func

def unescapedTag(name):
    def func(view):
        return unicode(view.get(name))
    return func

class EndOfSection(Exception):
    def __init__(self, template, position):
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

        # Standalone (non-interpolation) tags consume the entire line,
        # both leading whitespace and trailing newline.
        tagBeganLine = (not buffer[-1] or buffer[-1][-1] == '\n')
        tagEndedLine = (pos == len(template) or template[pos] == '\n')
        interpolationTag = captures['tag'] in ['', '&', '{']

        if (tagBeganLine and tagEndedLine and not interpolationTag):
            pos += 1
        elif captures['whitespace']:
            buffer.append(captures['whitespace'])
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
                tmpl = e.template
                pos  = e.position

            tag = { '#': sectionTag, '^': inverseTag }[captures['tag']]
            buffer.append(tag(name, tmpl, (self.otag, self.ctag)))
        elif captures['tag'] == '/':
            raise EndOfSection(template[index:match.end('whitespace')], pos)
        elif captures['tag'] in ['{', '&']:
            buffer.append(unescapedTag(name))
        elif captures['tag'] == '':
            buffer.append(escapedTag(name))
        else:
            raise Exception("'%s' is an unrecognized type!" % (captures['tag']))

        return pos

    def render(self, encoding=None):
        parsed = self._parse()
        result = ''.join(map(call(self.view), parsed))
        if encoding is not None:
            result = result.encode(encoding)

        return result
