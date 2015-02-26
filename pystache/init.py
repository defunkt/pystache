# encoding: utf-8

"""
This module contains the initialization logic called by __init__.py.

"""

from .parser import parse
from .renderer import Renderer
from .template_spec import TemplateSpec


def render(template, context=None, **kwargs):
    """
    Return the given template string rendered using the given context.

    """
    renderer = Renderer()
    return renderer.render(template, context, **kwargs)
