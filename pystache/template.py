import re
import cgi

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

    def _parse(self, template, section=None, index=0):
        """Parse a template into a syntax tree."""

        buffer = []
        pos = index

        while True:
            match = self.tag_re.search(template, pos)

            if match is None:
                break

            pos = self._handle_match(template, match, buffer)

        # Save the rest of the template.
        buffer.append(template[pos:])

        return buffer

    def _handle_match(self, template, match, buffer):
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

        # TODO: Process the remaining tag types.
        fetch = lambda view: view.get(captures['name'])

        if captures['tag'] == '!':
            pass
        elif captures['tag'] == '=':
            self.otag, self.ctag = captures['name'].split()
            self._compile_regexps()
        elif captures['tag'] in ['{', '&']:
            buffer.append(lambda view: unicode(fetch(view)))
        elif captures['tag'] == '':
            buffer.append(lambda view: cgi.escape(unicode(fetch(view)), True))
        else:
            raise

        return pos

    def render(self, encoding=None):
        parsed = self._parse(self.template)

        def call(x):
            return unicode(callable(x) and x(self.view) or x)

        result = ''.join(map(call, parsed))

        if encoding is not None:
            result = result.encode(encoding)

        return result
