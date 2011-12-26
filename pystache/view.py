# coding: utf-8

"""
This module provides a View class.

"""

import re
from types import UnboundMethodType

from .context import Context
from .loader import Loader
from .reader import Reader
from .renderer import Renderer


class View(object):

    template_name = None
    template_path = None
    template = None
    template_encoding = None
    template_extension = None

    _loader = None

    def __init__(self, template=None, context=None, loader=None, **kwargs):
        """
        Construct a View instance.

        Arguments:

          loader: the object (e.g. pystache.Loader or dictionary) responsible
            for loading templates during the rendering process, for example
            when loading partials.  The object should have a get() method
            that accepts a string and returns the corresponding template
            as a string, preferably as a unicode string.  The method should
            return None if there is no template with that name.

        """
        if loader is not None:
            self._loader = loader

        if template is not None:
            self.template = template

        _context = Context(self)
        if context:
            _context.push(context)
        if kwargs:
            _context.push(kwargs)

        self.context = _context

    def get_loader(self):
        if self._loader is None:
            # We delay setting self._loader until now (in the case that the
            # user did not supply a load_template to the constructor)
            # to let users set the template_extension attribute, etc. after
            # View.__init__() has already been called.
            reader = Reader(encoding=self.template_encoding)
            loader = Loader(search_dirs=self.template_path, reader=reader,
                            extension=self.template_extension)
            self._loader = loader

        return self._loader

    def load_template(self, template_name):
        loader = self.get_loader()
        return loader.get(template_name)

    def get_template(self):
        """
        Return the current template after setting it, if necessary.

        """
        if not self.template:
            template_name = self._get_template_name()
            self.template = self.load_template(template_name)

        return self.template

    def _get_template_name(self):
        """
        Return the name of the template to load.

        If the template_name attribute is not set, then this method constructs
        the template name from the class name as follows, for example:

            TemplatePartial => template_partial

        Otherwise, this method returns the template_name.

        """
        if self.template_name:
            return self.template_name

        template_name = self.__class__.__name__

        def repl(match):
            return '_' + match.group(0).lower()

        return re.sub('[A-Z]', repl, template_name)[1:]

    # TODO: the View class should probably have some sort of template renderer
    # associated with it to encapsulate all of the render-specific behavior
    # and options like encoding, escape, etc.  This would probably be better
    # than passing all of these options to render(), especially as the list
    # of possible options grows.
    def render(self, escape=None):
        """
        Return the view rendered using the current context.

        """
        loader = self.get_loader()
        template = self.get_template()
        renderer = Renderer(escape=escape, loader=loader)
        return renderer.render(template, self.context)

    def get(self, key, default=None):
        return self.context.get(key, default)

    def __str__(self):
        return self.render()
