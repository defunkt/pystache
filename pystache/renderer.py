# coding: utf-8

"""
This module provides a Template class.

"""

import cgi
import sys

from .context import Context
from .loader import Loader
from .renderengine import RenderEngine


markupsafe = None
try:
    import markupsafe
except ImportError:
    pass


class Renderer(object):

    # TODO: change load_template to load_partial.
    def __init__(self, load_template=None, output_encoding=None, escape=None,
                 default_encoding=None, decode_errors='strict'):
        """
        Construct an instance.

        Arguments:

          load_template: the function for loading partials.  The function should
            accept a single template_name parameter and return a template as
            a string.  Defaults to the default Loader's load_template() method.

          output_encoding: the encoding to use when rendering to a string.
            The argument should be the name of an encoding as a string, for
            example "utf-8".  See the render() method's documentation for more
            information.

          escape: the function used to escape mustache variable values
            when rendering a template.  The function should accept a unicode
            string and return an escaped string of the same type.  It need
            not handle strings of type `str` because this class will only
            pass it unicode strings.  The constructor assigns this escape
            function to the constructed instance's Template.escape() method.

            The argument defaults to markupsafe.escape when markupsafe is
            importable and cgi.escape otherwise.  To disable escaping entirely,
            one can pass `lambda s: s` as the escape function, for example.

          default_encoding: the name of the encoding to use when converting
            to unicode any strings of type `str` encountered during the
            rendering process.  The name will be passed as the "encoding"
            argument to the built-in function unicode().  Defaults to the
            encoding name returned by sys.getdefaultencoding().

          decode_errors: the string to pass as the "errors" argument to the
            built-in function unicode() when converting to unicode any
            strings of type `str` encountered during the rendering process.
            Defaults to "strict".

        """
        if load_template is None:
            loader = Loader()
            load_template = loader.load_template

        if default_encoding is None:
            default_encoding = sys.getdefaultencoding()

        if escape is None:
            escape = markupsafe.escape if markupsafe else cgi.escape

        literal = markupsafe.Markup if markupsafe else unicode

        self._literal = literal

        self.decode_errors = decode_errors
        self.default_encoding = default_encoding
        self.escape = escape
        self.load_template = load_template
        self.output_encoding = output_encoding

    def _unicode_and_escape(self, s):
        if not isinstance(s, unicode):
            s = self.unicode(s)
        return self.escape(s)

    def unicode(self, s):
        return unicode(s, self.default_encoding, self.decode_errors)

    def escape(self, u):
        """
        Escape a unicode string, and return it.

        This function is initialized as the escape function that was passed
        to the Template class's constructor when this instance was
        constructed.  See the constructor docstring for more information.

        """
        pass

    def literal(self, s):
        """
        Convert the given string to a unicode string, without escaping it.

        This function internally calls the built-in function unicode() and
        passes it the default_encoding and decode_errors attributes for this
        Template instance.  If markupsafe was importable when loading this
        module, this function returns an instance of the class
        markupsafe.Markup (which subclasses unicode).

        """
        return self._literal(self.unicode(s))

    def _make_context(self, context, **kwargs):
        """
        Initialize the context attribute.

        """
        if context is None:
            context = {}

        if isinstance(context, Context):
            context = context.copy()
        else:
            context = Context(context)

        if kwargs:
            context.push(kwargs)

        return context

    def _make_render_engine(self):
        """
        Return a RenderEngine instance for rendering.

        """
        engine = RenderEngine(load_template=self.load_template,
                              literal=self.literal,
                              escape=self._unicode_and_escape)
        return engine

    def render(self, template, context=None, **kwargs):
        """
        Render the given template using the given context.

        The return value is a unicode string, unless the output_encoding
        attribute has been set to a non-None value, in which case the
        return value has type str and is encoded using that encoding.

        If the template string is not unicode, it is first converted to
        unicode using the default_encoding and decode_errors attributes.
        See the Template constructor's docstring for more information.

        Arguments:

          template: a template string that is either unicode, or of type
            str and encoded using the encoding named by the default_encoding
            keyword argument.

          context: a dictionary, Context, or object (e.g. a View instance).

          **kwargs: additional key values to add to the context when rendering.
            These values take precedence over the context on any key conflicts.

        """
        engine = self._make_render_engine()
        context = self._make_context(context, **kwargs)

        if not isinstance(template, unicode):
            template = self.unicode(template)

        rendered = engine.render(template, context)

        if self.output_encoding is not None:
            rendered = rendered.encode(self.output_encoding)

        return rendered
