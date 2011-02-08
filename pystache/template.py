import re

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

            # Normalize the captures dictionary.
            captures = match.groupdict()
            if captures['change'] is not None:
                captures.update(tag='=', name=captures['delims'])
            elif captures['raw'] is not None:
                captures.update(tag='{', name=captures['raw_name'])

            # Save the literal text content.
            buffer.append(captures['content'])
            pos = match.end()

            # Save the whitespace following the text content.
            # TODO: Standalone tags should consume this.
            buffer.append(captures['whitespace'])

            # TODO: Process the remaining tag types.
            if captures['tag'] is '!':
                pass

        # Save the rest of the template.
        buffer.append(template[pos:])

        return buffer

    def _generate(self, parsed, view):
        """Convert a parse tree into a fully evaluated template."""

        # TODO: Handle non-trivial cases.
        return ''.join(parsed)

    def render(self, encoding=None):
        parsed = self._parse(self.template)
        result = self._generate(parsed, self.view)

        if encoding is not None:
            result = result.encode(encoding)

        return result
