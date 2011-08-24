# -*- coding: utf-8 -*-

"""
pystache.core
~~~~~~~~~~~~~

This module provides the main entrance point to Pystache.
"""


from .template import Template
from .view import View
from .loader import Loader


__all__ = ['Template', 'View', 'Loader', 'render']


def render(template, context=None, **kwargs):
    """Renders a template string against the given context."""

    context = context and context.copy() or {}
    context.update(kwargs)

    return Template(template, context).render()
