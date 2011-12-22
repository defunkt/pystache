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

    def _assert_render(self, expected, template, *context, **kwargs):
        engine = kwargs['engine'] if kwargs else self._engine()
        context = Context(*context)

        actual = engine.render(template, context)

        self.assertEquals(actual, expected)

    def test_init(self):
        """
        Test that __init__() stores all of the arguments correctly.

        """
        # In real-life, these arguments would be functions
        engine = RenderEngine(load_template="load_template", literal="literal", escape="escape")

        self.assertEquals(engine.escape, "escape")
        self.assertEquals(engine.literal, "literal")
        self.assertEquals(engine.load_template, "load_template")

    def test_render(self):
        self._assert_render('Hi Mom', 'Hi {{person}}', {'person': 'Mom'})

    def test_render_with_partial(self):
        partials = {'partial': "{{person}}"}
        engine = self._engine(partials)
        self._assert_render('Hi Mom', 'Hi {{>partial}}', {'person': 'Mom'}, engine=engine)
