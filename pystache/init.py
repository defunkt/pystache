# encoding: utf-8

"""
This module contains the initialization logic called by __init__.py.

"""

from .renderer import Renderer
from .view import View
from .loader import Loader


__all__ = ['render', 'Loader', 'Renderer', 'View']


def render(template, context=None, **kwargs):
    """
    Return the given template string rendered using the given context.

    """
    renderer = Renderer(template)
    return renderer.render(context, **kwargs)
