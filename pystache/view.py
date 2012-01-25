# coding: utf-8

"""
This module provides a View class.

"""

import os.path

from .context import Context
from .locator import Locator as TemplateLocator
from .reader import Reader
from .renderer import Renderer


# TODO: rename this class to something else (e.g. ITemplateInfo)
class View(object):

    """
    Subclass this class only if template customizations are needed.

    The following attributes allow one to customize/override template
    information on a per View basis.  A None value means to use default
    behavior and perform no customization.  All attributes are initially
    set to None.

    Attributes:

      template: the template to use, as a unicode string.

      template_path: the path to the template file, relative to the
        directory containing the module defining the class.

      template_dir: the directory containing the template file, relative
        to the directory containing the module defining the class.

      template_extension: the template file extension.  Defaults to "mustache".
        Pass False for no extension (i.e. extensionless template files).

    """

    template = None
    template_path = None

    template_directory = None
    template_name = None
    template_extension = None

    template_encoding = None

    _renderer = None

    locator = TemplateLocator()

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


class Locator(object):

    """
    A class for finding the template associated to a View instance.

    """

    # TODO: unit test this.
    def __init__(self, search_dirs, template_locator=None, reader=None):
        if reader is None:
            reader = Reader()

        if template_locator is None:
            template_locator = TemplateLocator()

        self.reader = reader
        self.search_dirs = search_dirs
        self.template_locator = template_locator

    def get_relative_template_location(self, view):
        """
        Return the relative template path as a (dir, file_name) pair.

        """
        if view.template_path is not None:
            return os.path.split(view.template_path)

        template_dir = view.template_directory

        # Otherwise, we don't know the directory.

        template_name = (view.template_name if view.template_name is not None else
                         self.template_locator.make_template_name(view))

        file_name = self.template_locator.make_file_name(template_name, view.template_extension)

        return (template_dir, file_name)

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
        """
        Return the unicode template string associated with a view.

        """
        if view.template is not None:
            return self.reader.unicode(view.template, view.template_encoding)

        path = self.get_template_path(view)

        return self.reader.read(path, view.template_encoding)
