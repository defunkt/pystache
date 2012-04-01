# coding: utf-8

"""
This module supports customized (aka special or specified) template loading.

"""

import os.path

from .context import Context
from .loader import Loader
from .locator import Locator
from .renderer import Renderer


# TODO: finish the class docstring.
class TemplateSpec(object):

    """
    A mixin or interface for specifying custom template information.

    The "spec" in TemplateSpec can be taken to mean that the template
    information is either "specified" or "special."

    A view should subclass this class only if customized template loading
    is needed.  The following attributes allow one to customize/override
    template information on a per view basis.  A None value means to use
    default behavior for that value and perform no customization.  All
    attributes are initialized to None.

    Attributes:

      template: the template as a string.

      template_rel_path: the path to the template file, relative to the
        directory containing the module defining the class.

      template_rel_directory: the directory containing the template file, relative
        to the directory containing the module defining the class.

      template_extension: the template file extension.  Defaults to "mustache".
        Pass False for no extension (i.e. extensionless template files).

    """

    template = None
    # TODO: remove template_path.
    template_path = None
    template_rel_path = None
    template_rel_directory = None
    template_name = None
    template_extension = None
    template_encoding = None


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


# TODO: get this class fully working with test cases, and then refactor
#   and replace the View class.
class SpecLoader(object):

    """
    Supports loading a custom-specified template.

    """

    def __init__(self, search_dirs=None, loader=None):
        if loader is None:
            loader = Loader()

        if search_dirs is None:
            search_dirs = []

        self.loader = loader
        self.search_dirs = search_dirs

    def _find_relative(self, spec):
        """
        Return the path to the template as a relative (dir, file_name) pair.

        The directory returned is relative to the directory containing the
        class definition of the given object.  The method returns None for
        this directory if the directory is unknown without first searching
        the search directories.

        """
        if spec.template_rel_path is not None:
            return os.path.split(spec.template_rel_path)

        # Otherwise, determine the file name separately.
        locator = self.loader._make_locator()

        template_name = (spec.template_name if spec.template_name is not None else
                         locator.make_template_name(spec))

        file_name = locator.make_file_name(template_name, spec.template_extension)

        return (spec.template_rel_directory, file_name)

    def _find(self, spec):
        """
        Find and return the path to the template associated to the instance.

        """
        dir_path, file_name = self._find_relative(spec)

        locator = self.loader._make_locator()

        if dir_path is None:
            # Then we need to search for the path.
            path = locator.find_object(spec, self.search_dirs, file_name=file_name)
        else:
            obj_dir = locator.get_object_directory(spec)
            path = os.path.join(obj_dir, dir_path, file_name)

        return path

    def load(self, spec):
        """
        Find and return the template associated to a TemplateSpec instance.

        Returns the template as a unicode string.

        Arguments:

          spec: a TemplateSpec instance.

        """
        if spec.template is not None:
            return self.loader.unicode(spec.template, spec.template_encoding)

        path = self._find(spec)

        return self.loader.read(path, spec.template_encoding)
