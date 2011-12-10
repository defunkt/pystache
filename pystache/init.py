# encoding: utf-8

from .template import Template
from .view import View
from .loader import Loader

__all__ = ['Template', 'View', 'Loader', 'render']


def render(template, context=None, **kwargs):

    context = context and context.copy() or {}
    context.update(kwargs)

    return Template(template, context).render()
