# coding: utf-8

"""
Provides a class for parsing template strings.

This module is only meant for internal use by the renderengine module.

"""

import re

from pystache.parsed import ParsedTemplate


DEFAULT_DELIMITERS = (u'{{', u'}}')
END_OF_LINE_CHARACTERS = [u'\r', u'\n']


def _compile_template_re(delimiters=None):
    """
    Return a regular expresssion object (re.RegexObject) instance.

    """
    if delimiters is None:
        delimiters = DEFAULT_DELIMITERS

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
          (?P<tag>[%(tag_types)s]?)  \s* (?P<tag_key>[\s\S]+?)
        )
        \s* %(ctag)s
    """ % {'tag_types': tag_types, 'otag': re.escape(delimiters[0]), 'ctag': re.escape(delimiters[1])}

    return re.compile(tag, re.VERBOSE)


class ParsingError(Exception):

    pass


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

    def parse(self, template, start_index=0, section_key=None):
        """
        Parse a template string starting at some index.

        This method uses the current tag delimiter.

        Arguments:

          template: a unicode string that is the template to parse.

          index: the index at which to start parsing.

        Returns:

          a ParsedTemplate instance.

        """
        parse_tree = []
        index = start_index

        content_end_index, parsed_section = None, None

        while True:
            match = self._template_re.search(template, index)

            if match is None:
                break

            match_index = match.start()
            end_index = match.end()

            before_tag = template[index : match_index]

            parse_tree.append(before_tag)

            matches = match.groupdict()

            # Normalize the matches dictionary.
            if matches['change'] is not None:
                matches.update(tag='=', tag_key=matches['delims'])
            elif matches['raw'] is not None:
                matches.update(tag='&', tag_key=matches['raw_name'])

            tag_type = matches['tag']
            tag_key = matches['tag_key']
            leading_whitespace = matches['whitespace']

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
            elif leading_whitespace:
                parse_tree.append(leading_whitespace)
                match_index += len(leading_whitespace)
                leading_whitespace = ''

            if tag_type == '/':
                if tag_key != section_key:
                    raise ParsingError("Section end tag mismatch: %s != %s" % (tag_key, section_key))

                return end_index, ParsedTemplate(parse_tree), match_index

            if tag_type in ('#', '^'):
                index, parsed_section, content_end_index = self.parse(template, end_index, tag_key)
            else:
                index = end_index
            # Variable index is now the next character to process.

            self._handle_tag_type(template, parse_tree, tag_type, tag_key, leading_whitespace,
                                  end_index, content_end_index, parsed_section)

        # Save the rest of the template.
        parse_tree.append(template[index:])

        return ParsedTemplate(parse_tree)

    def _handle_tag_type(self, template, parse_tree, tag_type, tag_key, leading_whitespace,
                         section_start_index, section_end_index, parsed_section):

        # TODO: switch to using a dictionary instead of a bunch of ifs and elifs.
        if tag_type == '!':
            return

        if tag_type == '=':
            delimiters = tag_key.split()
            self._change_delimiters(delimiters)
            return

        if tag_type == '':

            func = self.engine._make_get_escaped(tag_key)

        elif tag_type == '&':

            func = self.engine._make_get_literal(tag_key)

        elif tag_type == '#':

            func = self.engine._make_get_section(tag_key, parsed_section, self._delimiters,
                                                 template, section_start_index, section_end_index)

        elif tag_type == '^':

            func = self.engine._make_get_inverse(tag_key, parsed_section)

        elif tag_type == '>':

            func = self.engine._make_get_partial(tag_key, leading_whitespace)

        else:

            raise Exception("Unrecognized tag type: %s" % repr(tag_type))

        parse_tree.append(func)
