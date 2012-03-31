# encoding: utf-8

"""
This module contains the initialization logic called by __init__.py.

"""

from .template_spec import View
from .template_spec import  TemplateSpec
from .renderer import Renderer


__all__ = ['render', 'Renderer', 'View', 'TemplateSpec']


def render(template, context=None, **kwargs):
    """
    Return the given template string rendered using the given context.

    """
    renderer = Renderer()
    return renderer.render(template, context, **kwargs)
