# coding: utf-8

"""
This module exposes the deprecated View class.

TODO: remove this module.

"""

from .context import Context
from .locator import Locator
from .renderer import Renderer
from .template_spec import TemplateSpec


# TODO: remove this class.
class View(TemplateSpec):

    _renderer = None

    locator = Locator()

    def __init__(self, context=None):
        """
        Construct a View instance.

        """
        context = Context.create(self, context)

        self.context = context

    def _get_renderer(self):
        if self._renderer is None:
            # We delay setting self._renderer until now (instead of, say,
            # setting it in the constructor) in case the user changes after
            # instantiation some of the attributes on which the Renderer
            # depends.  This lets users set the template_extension attribute,
            # etc. after View.__init__() has already been called.
            renderer = Renderer(file_encoding=self.template_encoding,
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
