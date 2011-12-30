# coding: utf-8

"""
This module provides a View class.

"""

from .context import Context
from .locator import Locator
from .renderer import Renderer


class View(object):

    template_name = None
    template_path = None
    template = None
    template_encoding = None
    template_extension = None

    _renderer = None

    locator = Locator()

    def __init__(self, template=None, context=None, partials=None, **kwargs):
        """
        Construct a View instance.

        Arguments:

          partials: a custom object (e.g. dictionary) responsible for
            loading partials during the rendering process.  The object
            should have a get() method that accepts a string and returns
            the corresponding template as a string, preferably as a
            unicode string.  The method should return None if there is
            no template with that name, or raise an exception.

        """
        if template is not None:
            self.template = template

        context = Context.create(self, context, **kwargs)

        self._partials = partials

        self.context = context

    def _get_renderer(self):
        if self._renderer is None:
            # We delay setting self._renderer until now (instead of, say,
            # setting it in the constructor) in case the user changes after
            # instantiation some of the attributes on which the Renderer
            # depends.  This lets users set the template_extension attribute,
            # etc. after View.__init__() has already been called.
            renderer = Renderer(partials=self._partials,
                                file_encoding=self.template_encoding,
                                search_dirs=self.template_path,
                                file_extension=self.template_extension)
            self._renderer = renderer

        return self._renderer

    def get_template(self):
        """
        Return the current template after setting it, if necessary.

        """
        if not self.template:
            template_name = self._get_template_name()
            renderer = self._get_renderer()
            self.template = renderer.load_template(template_name)

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

        return self.locator.make_template_name(self)

    def render(self):
        """
        Return the view rendered using the current context.

        """
        template = self.get_template()
        renderer = self._get_renderer()
        return renderer.render(template, self.context)

    def get(self, key, default=None):
        return self.context.get(key, default)

    def __str__(self):
        return self.render()
