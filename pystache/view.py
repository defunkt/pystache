# coding: utf-8

"""
This module provides a View class.

"""

import os.path

from .context import Context
from .locator import Locator as TemplateLocator
from .renderer import Renderer


# TODO: rename this class to something else (e.g. ITemplateInfo)
class View(object):

    template_name = None
    template_path = None
    template = None
    template_encoding = None
    template_extension = None

    _renderer = None

    locator = TemplateLocator()

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


class Locator(object):

    """
    A class for finding the template associated to a View instance.

    """

    def __init__(self, reader, search_dirs, template_locator):
        self.reader = reader
        self.search_dirs = search_dirs
        self.template_locator = template_locator

    # TODO: unit test
    def get_relative_template_location(self, view):
        """
        Return the relative template path as a (dir, file_name) pair.

        """
        if view.template_path is not None:
            return os.path.split(view.template_path)


        # TODO: finish this
        return (None, None)

    def get_template_path(self, view):
        """
        Return the path to the view's associated template.

        """
        dir_path, file_name = self.get_relative_template_location(view)

        if dir_path is None:
            # Then we need to search for the path.
            path = self.template_locator.find_path_by_object(self.search_dirs, view, file_name=file_name)
        else:
            obj_dir = self.template_locator.get_object_directory(view)
            path = os.path.join(obj_dir, dir_path, file_name)

        return path

    def get_template(self, view):
        if view.template is not None:
            return view.template

        path = self.get_template_path(view)

        return self.reader.read(path)
