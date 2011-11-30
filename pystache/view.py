# -*- coding: utf-8 -*-

"""
pystache.loader
~~~~~~~~~~~~~~~

This module provides Pystache's views.
"""

import re
from types import UnboundMethodType

from .loader import Loader
from .template import Template



class View(object):
    """A Pystache view."""

    template_name = None
    template_path = None
    template = None
    template_encoding = None
    template_extension = 'mustache'

    def __init__(self, template=None, context=None, **kwargs):

        self.template = template

        context = context or {}
        context.update(kwargs)

        self.context_list = [context]


    def get(self, attr, default=None):
        """Returns given attribute value from View."""

        attr = get_or_attr(self.context_list, attr, getattr(self, attr, default))

        if hasattr(attr, '__call__') and type(attr) is UnboundMethodType:
            return attr()
        else:
            return attr


    def get_template(self, template_name):
        """Returns current Template."""

        if not self.template:

            template_name = self._get_template_name(template_name)

            self.template = Loader().load_template(
                template_name,
                self.template_path,
                encoding=self.template_encoding,
                extension=self.template_extension)

        return self.template


    def _get_template_name(self, template_name=None):
        """TemplatePartial => template_partial
        Takes a string but defaults to using the current class' name or
        the `template_name` attribute.
        """

        if template_name:
            return template_name

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
        """Returns rendered Template."""

        template = Template(self.get_template(self.template_name), self)
        return template.render(encoding=encoding)


    def __contains__(self, needle):
        return needle in self.context or hasattr(self, needle)


    def __getitem__(self, attr):
        val = self.get(attr, None)

        if not val and val is not 0:
            raise KeyError("Key '%s' does not exist in View" % attr)
        return val


    def __getattr__(self, attr):
        if attr == 'context':
            return self._get_context()

        raise AttributeError("Attribute '%s' does not exist in View" % attr)


    def __str__(self):
        return self.render()



def get_or_attr(context_list, name, default=None):
    """Returns an attribute from given context."""

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


