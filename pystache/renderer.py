# coding: utf-8

"""
This module provides a Renderer class to render templates.

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

    def __init__(self, output_encoding=None, escape=None,
                 default_encoding=None, decode_errors='strict', load_template=None):
        """
        Construct an instance.

        Arguments:

          output_encoding: the encoding to use when rendering to a string.
            The argument should be the name of an encoding as a string, for
            example "utf-8".  See the render() method's documentation for
            more information.

          escape: the function used to escape mustache variable values
            when rendering a template.  The function should accept a
            unicode string and return an escaped string of the same type.
                This function need not handle strings of type `str` because
            this class will only pass it unicode strings.  The constructor
            assigns this function to the constructed instance's escape()
            method.
                The argument defaults to markupsafe.escape when markupsafe
            is importable and cgi.escape otherwise.  To disable escaping
            entirely, one can pass `lambda u: u` as the escape function,
            for example.

          default_encoding: the name of the encoding to use when converting
            to unicode any strings of type `str` encountered during the
            rendering process.  The name will be passed as the "encoding"
            argument to the built-in function unicode().  Defaults to the
            encoding name returned by sys.getdefaultencoding().

          decode_errors: the string to pass as the "errors" argument to the
            built-in function unicode() when converting to unicode any
            strings of type `str` encountered during the rendering process.
            Defaults to "strict".

          load_template: a function for loading templates by name, for
            example when loading partials.  The function should accept a
            single template_name parameter and return a template as a string.
            Defaults to the default Loader's get() method.

        """
        if default_encoding is None:
            default_encoding = sys.getdefaultencoding()

        if escape is None:
            escape = markupsafe.escape if markupsafe else cgi.escape

        if load_template is None:
            loader = Loader()
            load_template = loader.get

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

    def _make_load_partial(self):
        """
        Return the load_partial function for use by RenderEngine.

        """
        def load_partial(name):
            template = self.load_template(name)
            # Make sure the return value of load_template is unicode since
            # RenderEngine requires it.  Also, check that the string is not
            # already unicode to avoid "double-decoding".  Otherwise, we
            # would get the following error:
            #   TypeError: decoding Unicode is not supported
            if not isinstance(template, unicode):
                template = self.unicode(template)

            return template

        return load_partial

    def _make_render_engine(self):
        """
        Return a RenderEngine instance for rendering.

        """
        load_partial = self._make_load_partial()

        engine = RenderEngine(load_partial=load_partial,
                              literal=self.literal,
                              escape=self._unicode_and_escape)
        return engine

    def render(self, template, context=None, **kwargs):
        """
        Render the given template using the given context.

        Returns:

          If the output_encoding attribute is None, the return value is
          a unicode string.  Otherwise, the return value is encoded to a
          string of type str using the output encoding named by the
          output_encoding attribute.

        Arguments:

          template: a template string that is either unicode or of type str.
            If the string has type str, it is first converted to unicode
            using the default_encoding and decode_errors attributes of this
            instance.  See the constructor docstring for more information.

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
