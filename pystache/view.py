# coding: utf-8

"""
This module provides a View class.

"""

import re
from types import UnboundMethodType

from .loader import Loader
from .template import Template


def get_or_attr(context_list, name, default=None):
    """
    Find and return an attribute from the given context.

    """
    if not context_list:
        return default

    for obj in context_list:
        try:
            return obj[name]
        except KeyError:
            pass
        except:
            try:
                return getattr(obj, name)
            except AttributeError:
                pass

    return default


class View(object):

    template_name = None
    template_path = None
    template = None
    template_encoding = None
    template_extension = 'mustache'

    # A function that accepts a single template_name parameter.
    _load_template = None

    def __init__(self, template=None, context=None, load_template=None, **kwargs):
        """
        Construct a View instance.

        """
        if load_template is not None:
            self._load_template = load_template

        if template is not None:
            self.template = template

        context = context or {}
        context.update(**kwargs)

        self.context_list = [context]

    def get(self, attr, default=None):
        """
        Return the value for the given attribute.

        """
        attr = get_or_attr(self.context_list, attr, getattr(self, attr, default))

        if hasattr(attr, '__call__') and type(attr) is UnboundMethodType:
            return attr()
        else:
            return attr

    def load_template(self, template_name):
        if self._load_template is None:
            # We delay setting self._load_template until now (in the case
            # that the user did not supply a load_template to the constructor)
            # to let users set the template_extension attribute, etc. after
            # View.__init__() has already been called.
            loader = Loader(search_dirs=self.template_path, encoding=self.template_encoding,
                            extension=self.template_extension)
            self._load_template = loader.load_template

        return self._load_template(template_name)

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
        Return the name of this Template instance.

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

    def _get_context(self):
        context = {}
        for item in self.context_list:
            if hasattr(item, 'keys') and hasattr(item, '__getitem__'):
                context.update(item)
        return context

    def render(self, encoding=None):
        """
        Return the view rendered using the current context.

        """
        template = Template(self.get_template(), self)
        return template.render(encoding=encoding)

    def __contains__(self, needle):
        return needle in self.context or hasattr(self, needle)

    def __getitem__(self, attr):
        val = self.get(attr, None)

        # We use "==" rather than "is" to compare integers, as using "is" relies
        # on an implementation detail of CPython.  The test about rendering
        # zeroes fails on PyPy when using "is".
        # See issue #34: https://github.com/defunkt/pystache/issues/34
        if not val and val != 0:
            raise KeyError("Key '%s' does not exist in View" % attr)
        return val

    def __getattr__(self, attr):
        if attr == 'context':
            return self._get_context()

        raise AttributeError("Attribute '%s' does not exist in View" % attr)

    def __str__(self):
        return self.render()
