# encoding: utf-8

"""
This module contains the initialization logic called by __init__.py.

"""

from .custom_template import View
from .custom_template import  CustomizedTemplate
from .renderer import Renderer


__all__ = ['render', 'Renderer', 'View', 'CustomizedTemplate']


def render(template, context=None, **kwargs):
    """
    Return the given template string rendered using the given context.

    """
    renderer = Renderer()
    return renderer.render(template, context, **kwargs)
