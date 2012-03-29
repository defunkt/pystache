# coding: utf-8

"""
This module provides a Renderer class to render templates.

"""

import cgi
import os
import sys

from . import defaults
from .context import Context
from .loader import Loader
from .renderengine import RenderEngine


# The quote=True argument causes double quotes to be escaped,
# but not single quotes:
#   http://docs.python.org/library/cgi.html#cgi.escape
DEFAULT_ESCAPE = lambda s: cgi.escape(s, quote=True)


class Renderer(object):

    """
    A class for rendering mustache templates.

    This class supports several rendering options which are described in
    the constructor's docstring.  Among these, the constructor supports
    passing a custom partial loader.

    Here is an example of rendering a template using a custom partial loader
    that loads partials from a string-string dictionary.

    >>> partials = {'partial': 'Hello, {{thing}}!'}
    >>> renderer = Renderer(partials=partials)
    >>> renderer.render('{{>partial}}', {'thing': 'world'})
    u'Hello, world!'

    """

    def __init__(self, file_encoding=None, default_encoding=None,
                 decode_errors=None, search_dirs=None, file_extension=None,
                 escape=None, partials=None):
        """
        Construct an instance.

        Arguments:

          partials: an object (e.g. a dictionary) for custom partial loading
            during the rendering process.
                The object should have a get() method that accepts a string
            and returns the corresponding template as a string, preferably
            as a unicode string.  If there is no template with that name,
            the get() method should either return None (as dict.get() does)
            or raise an exception.
                If this argument is None, the rendering process will use
            the normal procedure of locating and reading templates from
            the file system -- using relevant instance attributes like
            search_dirs, file_encoding, etc.

          escape: the function used to escape variable tag values when
            rendering a template.  The function should accept a unicode
            string (or subclass of unicode) and return an escaped string
            that is again unicode (or a subclass of unicode).
                This function need not handle strings of type `str` because
            this class will only pass it unicode strings.  The constructor
            assigns this function to the constructed instance's escape()
            method.
                The argument defaults to `cgi.escape(s, quote=True)`.  To
            disable escaping entirely, one can pass `lambda u: u` as the
            escape function, for example.  One may also wish to consider
            using markupsafe's escape function: markupsafe.escape().

          file_encoding: the name of the encoding of all template files.
            This encoding is used when reading and converting any template
            files to unicode.  All templates are converted to unicode prior
            to parsing.  Defaults to the default_encoding argument.

          default_encoding: the name of the encoding to use when converting
            to unicode any strings of type str encountered during the
            rendering process.  The name will be passed as the encoding
            argument to the built-in function unicode().  Defaults to the
            encoding name returned by sys.getdefaultencoding().

          decode_errors: the string to pass as the errors argument to the
            built-in function unicode() when converting str strings to
            unicode.  Defaults to the package default.

          search_dirs: the list of directories in which to search for
            templates when loading a template by name.  Defaults to the
            current working directory.  If given a string, the string is
            interpreted as a single directory.

          file_extension: the template file extension.  Pass False for no
            extension (i.e. to use extensionless template files).
            Defaults to the package default.

        """
        if decode_errors is None:
            decode_errors = defaults.DECODE_ERRORS

        if default_encoding is None:
            default_encoding = sys.getdefaultencoding()

        if escape is None:
            escape = DEFAULT_ESCAPE

        # This needs to be after we set the default default_encoding.
        if file_encoding is None:
            file_encoding = default_encoding

        if file_extension is None:
            file_extension = defaults.TEMPLATE_EXTENSION

        if search_dirs is None:
            search_dirs = os.curdir  # i.e. "."

        if isinstance(search_dirs, basestring):
            search_dirs = [search_dirs]

        self.decode_errors = decode_errors
        self.default_encoding = default_encoding
        self.escape = escape
        self.file_encoding = file_encoding
        self.file_extension = file_extension
        self.partials = partials
        self.search_dirs = search_dirs

    def _to_unicode_soft(self, s):
        """
        Convert a basestring to unicode, preserving any unicode subclass.

        """
        # Avoid the "double-decoding" TypeError.
        return s if isinstance(s, unicode) else self.unicode(s)

    def _to_unicode_hard(self, s):
        """
        Convert a basestring to a string with type unicode (not subclass).

        """
        return unicode(self._to_unicode_soft(s))

    def _escape_to_unicode(self, s):
        """
        Convert a basestring to unicode (preserving any unicode subclass), and escape it.

        Returns a unicode string (not subclass).

        """
        return unicode(self.escape(self._to_unicode_soft(s)))

    def unicode(self, s):
        """
        Convert a string to unicode, using default_encoding and decode_errors.

        Raises:

          TypeError: Because this method calls Python's built-in unicode()
            function, this method raises the following exception if the
            given string is already unicode:

              TypeError: decoding Unicode is not supported

        """
        # TODO: Wrap UnicodeDecodeErrors with a message about setting
        # the default_encoding and decode_errors attributes.
        return unicode(s, self.default_encoding, self.decode_errors)

    def _make_loader(self):
        """
        Create a Loader instance using current attributes.

        """
        return Loader(encoding=self.file_encoding, decode_errors=self.decode_errors,
                      extension=self.file_extension)

    def _make_load_template(self):
        """
        Return a function that loads a template by name.

        """
        loader = self._make_loader()

        def load_template(template_name):
            return loader.load_name(template_name, self.search_dirs)

        return load_template

    def _make_load_partial(self):
        """
        Return the load_partial function to pass to RenderEngine.__init__().

        """
        if self.partials is None:
            load_template = self._make_load_template()
            return load_template

        # Otherwise, create a load_partial function from the custom partial
        # loader that satisfies RenderEngine requirements (and that provides
        # a nicer exception, etc).
        partials = self.partials

        def load_partial(name):
            template = partials.get(name)

            if template is None:
                # TODO: make a TemplateNotFoundException type that provides
                # the original partials as an attribute.
                raise Exception("Partial not found with name: %s" % repr(name))

            # RenderEngine requires that the return value be unicode.
            return self._to_unicode_hard(template)

        return load_partial

    def _make_render_engine(self):
        """
        Return a RenderEngine instance for rendering.

        """
        load_partial = self._make_load_partial()

        engine = RenderEngine(load_partial=load_partial,
                              literal=self._to_unicode_hard,
                              escape=self._escape_to_unicode)
        return engine

    # TODO: add unit tests for this method.
    def load_template(self, template_name):
        """
        Load a template by name from the file system.

        """
        load_template = self._make_load_template()
        return load_template(template_name)

    def _render_string(self, template, *context, **kwargs):
        """
        Render the given template string using the given context.

        """
        # RenderEngine.render() requires that the template string be unicode.
        template = self._to_unicode_hard(template)

        context = Context.create(*context, **kwargs)

        engine = self._make_render_engine()
        rendered = engine.render(template, context)

        return unicode(rendered)

    def _render_object(self, obj, *context, **kwargs):
        """
        Render the template associated with the given object.

        """
        loader = self._make_loader()
        template = loader.load_object(obj, self.search_dirs)

        context = [obj] + list(context)

        return self._render_string(template, *context, **kwargs)

    def render_path(self, template_path, *context, **kwargs):
        """
        Render the template at the given path using the given context.

        Read the render() docstring for more information.

        """
        loader = self._make_loader()
        template = loader.read(template_path)

        return self._render_string(template, *context, **kwargs)

    def render(self, template, *context, **kwargs):
        """
        Render the given template (or template object) using the given context.

        Returns the rendering as a unicode string.

        Prior to rendering, templates of type str are converted to unicode
        using the default_encoding and decode_errors attributes.  See the
        constructor docstring for more information.

        Arguments:

          template: a template string of type unicode or str, or an object
            instance.  If the argument is an object, the function first looks
            for the template associated to the object by calling this class's
            get_associated_template() method.  The rendering process also
            uses the passed object as the first element of the context stack
            when rendering.

          *context: zero or more dictionaries, Context instances, or objects
            with which to populate the initial context stack.  None
            arguments are skipped.  Items in the *context list are added to
            the context stack in order so that later items in the argument
            list take precedence over earlier items.

          **kwargs: additional key-value data to add to the context stack.
            As these arguments appear after all items in the *context list,
            in the case of key conflicts these values take precedence over
            all items in the *context list.

        """
        if not isinstance(template, basestring):
            # Then we assume the template is an object.
            return self._render_object(template, *context, **kwargs)

        return self._render_string(template, *context, **kwargs)
