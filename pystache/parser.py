# coding: utf-8

"""
Provides a class for parsing template strings.

This module is only meant for internal use by the renderengine module.

"""

import re


DEFAULT_DELIMITERS = ('{{', '}}')
END_OF_LINE_CHARACTERS = ['\r', '\n']


def _compile_template_re(delimiters):

    # The possible tag type characters following the opening tag,
    # excluding "=" and "{".
    tag_types = "!>&/#^"

    # TODO: are we following this in the spec?
    #
    #   The tag's content MUST be a non-whitespace character sequence
    #   NOT containing the current closing delimiter.
    #
    tag = r"""
        (?P<whitespace>[\ \t]*)
        %(otag)s \s*
        (?:
          (?P<change>=) \s* (?P<delims>.+?)   \s* = |
          (?P<raw>{)    \s* (?P<raw_name>.+?) \s* } |
          (?P<tag>[%(tag_types)s]?)  \s* (?P<name>[\s\S]+?)
        )
        \s* %(ctag)s
    """ % {'tag_types': tag_types, 'otag': re.escape(delimiters[0]), 'ctag': re.escape(delimiters[1])}

    return re.compile(tag, re.VERBOSE)


class EndOfSection(Exception):
    def __init__(self, parse_tree, template, position):
        self.parse_tree = parse_tree
        self.template = template
        self.position = position


class Parser(object):

    _delimiters = None
    _template_re = None

    def __init__(self, engine, delimiters=None):
        """
        Construct an instance.

        Arguments:

          engine: a RenderEngine instance.

        """
        if delimiters is None:
            delimiters = DEFAULT_DELIMITERS

        self._delimiters = delimiters
        self.engine = engine

    def compile_template_re(self):
        self._template_re = _compile_template_re(self._delimiters)

    def _change_delimiters(self, delimiters):
        self._delimiters = delimiters
        self.compile_template_re()

    def parse(self, template, index=0):
        """
        Parse a template string into a syntax tree using current attributes.

        This method uses the current RenderEngine instance's attributes,
        including the current tag delimiter, etc.

        """
        parse_tree = []
        start_index = index

        while True:
            match = self._template_re.search(template, index)

            if match is None:
                break

            match_index = match.start()
            end_index = match.end()

            before_tag = template[index : match_index]

            parse_tree.append(before_tag)

            matches = match.groupdict()

            index = self._handle_match(template, parse_tree, matches, start_index, match_index, end_index)

        # Save the rest of the template.
        parse_tree.append(template[index:])

        return parse_tree

    def _handle_match(self, template, parse_tree, matches, start_index, match_index, end_index):

        engine = self.engine

        # Normalize the matches dictionary.
        if matches['change'] is not None:
            matches.update(tag='=', name=matches['delims'])
        elif matches['raw'] is not None:
            matches.update(tag='&', name=matches['raw_name'])

        tag_type = matches['tag']

        # Standalone (non-interpolation) tags consume the entire line,
        # both leading whitespace and trailing newline.
        did_tag_begin_line = match_index == 0 or template[match_index - 1] in END_OF_LINE_CHARACTERS
        did_tag_end_line = end_index == len(template) or template[end_index] in END_OF_LINE_CHARACTERS
        is_tag_interpolating = tag_type in ['', '&']

        if did_tag_begin_line and did_tag_end_line and not is_tag_interpolating:
            if end_index < len(template):
                end_index += template[end_index] == '\r' and 1 or 0
            if end_index < len(template):
                end_index += template[end_index] == '\n' and 1 or 0
        elif matches['whitespace']:
            parse_tree.append(matches['whitespace'])
            match_index += len(matches['whitespace'])
            matches['whitespace'] = ''

        name = matches['name']

        if tag_type == '!':
            return end_index

        if tag_type == '=':
            delimiters = name.split()
            self._change_delimiters(delimiters)
            return end_index

        if tag_type == '>':
            func = engine._make_get_partial(name, matches['whitespace'])
        elif tag_type in ['#', '^']:

            try:
                self.parse(template=template, index=end_index)
            except EndOfSection as e:
                bufr = e.parse_tree
                tmpl = e.template
                end_index = e.position

            if tag_type == '#':
                func = engine._make_get_section(name, bufr, tmpl, self._delimiters)
            else:
                func = engine._make_get_inverse(name, bufr)

        elif tag_type == '&':

            func = engine._make_get_literal(name)

        elif tag_type == '':

            func = engine._make_get_escaped(name)

        elif tag_type == '/':

            # TODO: don't use exceptions for flow control.
            raise EndOfSection(parse_tree, template[start_index:match_index], end_index)

        else:
            raise Exception("Unrecognized tag type: %s" % repr(tag_type))

        parse_tree.append(func)

        return end_index

