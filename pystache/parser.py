# coding: utf-8

"""
Provides a class for parsing template strings.

This module is only meant for internal use by the renderengine module.

"""

import re

from pystache.parsed import ParsedTemplate


DEFAULT_DELIMITERS = (u'{{', u'}}')
END_OF_LINE_CHARACTERS = [u'\r', u'\n']
NON_BLANK_RE = re.compile(ur'^(.)', re.M)


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


## Node types


class CommentNode(object):

    def render(self, engine, context):
        return u''


class ChangeNode(object):

    def __init__(self, delimiters):
        self.delimiters = delimiters

    def render(self, engine, context):
        return u''


class VariableNode(object):

    def __init__(self, key):
        self.key = key

    def render(self, engine, context):
        s = engine.fetch_string(context, self.key)
        return engine.escape(s)


class LiteralNode(object):

    def __init__(self, key):
        self.key = key

    def render(self, engine, context):
        s = engine.fetch_string(context, self.key)
        return engine.literal(s)


class PartialNode(object):

    def __init__(self, key, indent):
        self.key = key
        self.indent = indent

    def render(self, engine, context):
        template = engine.resolve_partial(self.key)
        # Indent before rendering.
        template = re.sub(NON_BLANK_RE, self.indent + ur'\1', template)

        return engine.render(template, context)


class InvertedNode(object):

    def __init__(self, key, parsed_section):
        self.key = key
        self.parsed_section = parsed_section

    def render(self, engine, context):
        # TODO: is there a bug because we are not using the same
        #   logic as in fetch_string()?
        data = engine.resolve_context(context, self.key)
        # Note that lambdas are considered truthy for inverted sections
        # per the spec.
        if data:
            return u''
        return engine._render_parsed(self.parsed_section, context)


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

    def _compile_delimiters(self):
        self._template_re = _compile_template_re(self._delimiters)

    def _change_delimiters(self, delimiters):
        self._delimiters = delimiters
        self._compile_delimiters()

    def parse(self, template):
        """
        Parse a template string starting at some index.

        This method uses the current tag delimiter.

        Arguments:

          template: a unicode string that is the template to parse.

          index: the index at which to start parsing.

        Returns:

          a ParsedTemplate instance.

        """
        self._compile_delimiters()

        start_index = 0
        content_end_index, parsed_section, section_key = None, None, None
        parsed_template = ParsedTemplate()

        states = []

        while True:
            match = self._template_re.search(template, start_index)

            if match is None:
                break

            match_index = match.start()
            end_index = match.end()

            # Avoid adding spurious empty strings to the parse tree.
            if start_index != match_index:
                parsed_template.add(template[start_index:match_index])

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
                parsed_template.add(leading_whitespace)
                match_index += len(leading_whitespace)
                leading_whitespace = ''

            start_index = end_index

            if tag_type in ('#', '^'):
                # Cache current state.
                state = (tag_type, end_index, section_key, parsed_template)
                states.append(state)

                # Initialize new state
                section_key, parsed_template = tag_key, ParsedTemplate()
                continue

            if tag_type == '/':
                if tag_key != section_key:
                    raise ParsingError("Section end tag mismatch: %s != %s" % (tag_key, section_key))

                # Restore previous state with newly found section data.
                parsed_section = parsed_template

                (tag_type, section_start_index, section_key, parsed_template) = states.pop()
                node = self._make_section_node(template, tag_type, tag_key, parsed_section,
                                               section_start_index, match_index)

            else:
                node = self._make_interpolation_node(tag_type, tag_key, leading_whitespace)

            parsed_template.add(node)

        # Add the remainder of the template.
        parsed_template.add(template[start_index:])

        return parsed_template

    def _make_interpolation_node(self, tag_type, tag_key, leading_whitespace):
        """
        Create and return a non-section node for the parse tree.

        """
        # TODO: switch to using a dictionary instead of a bunch of ifs and elifs.
        if tag_type == '!':
            return CommentNode()

        if tag_type == '=':
            delimiters = tag_key.split()
            self._change_delimiters(delimiters)
            return ChangeNode(delimiters)

        if tag_type == '':
            return VariableNode(tag_key)

        if tag_type == '&':
            return LiteralNode(tag_key)

        if tag_type == '>':
            return PartialNode(tag_key, leading_whitespace)

        raise Exception("Invalid symbol for interpolation tag: %s" % repr(tag_type))

    def _make_section_node(self, template, tag_type, tag_key, parsed_section,
                           section_start_index, section_end_index):
        """
        Create and return a section node for the parse tree.

        """
        if tag_type == '#':
            return self.engine._make_get_section(tag_key, parsed_section, self._delimiters,
                                                 template, section_start_index, section_end_index)

        if tag_type == '^':
            return InvertedNode(tag_key, parsed_section)

        raise Exception("Invalid symbol for section tag: %s" % repr(tag_type))
