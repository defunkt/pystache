# coding: utf-8

"""
Unit tests of renderengine.py.

"""

import cgi
import unittest

from pystache.context import Context
from pystache.renderengine import RenderEngine


class RenderEngineTestCase(unittest.TestCase):

    """Test the RenderEngine class."""

    def _engine(self, partials=None):
        """
        Create and return a default RenderEngine for testing.

        """
        load_template = None
        to_unicode = unicode

        escape = lambda s: cgi.escape(to_unicode(s))
        literal = to_unicode

        if partials is not None:
            load_template = lambda key: partials[key]

        engine = RenderEngine(literal=literal, escape=escape, load_template=load_template)
        return engine

    def _assert_render(self, engine, expected, template, *context):
        if engine is None:
            engine = self._engine()

        context = Context(*context)

        actual = engine.render(template, context)
        self.assertEquals(actual, expected)

    def test_render(self):
        self._assert_render(None, 'Hi Mom', 'Hi {{person}}', {'person': 'Mom'})

    def test_render_with_partial(self):
        partials = {'partial': "{{person}}"}
        engine = self._engine(partials)
        self._assert_render(engine, 'Hi Mom', 'Hi {{>partial}}', {'person': 'Mom'})
