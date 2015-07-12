#! -*- coding: utf-8 -*-
"""
pystache meets handlebars
FIXME: doc copyright & licencing
"""
from pystache.context import KeyNotFoundError
import pystache.renderengine
import pystache.renderer
import pystache
import decimal

class Renderer(pystache.Renderer):
    """ pystache renderer augmented with handlebars style helpers

    >>> from pystache import handlebars
    >>> renderer = handlebars.Renderer()
    >>> def show(res):
    ...     print("'%s'" % res)
    >>> show(renderer.render("{{plain}}", {'plain': 'Hello'}))
    'Hello'
    >>> show(renderer.render("{{plain}}", {'plain': 1.2}))
    '1.2'
    >>> import operator
    >>> def ljust(a, n, c=' '):
    ...     return str(a).ljust(n, c)
    >>> renderer.register_helper('lj', ljust)
    >>> renderer.register_helper('+', operator.add)
    >>> show(renderer.render("{{lj income 7 '0'}}", {'income':'30000'}))
    '3000000'
    >>> show(renderer.render("{{lj '' a '0'}}", {'a': 7}))
    '0000000'
    >>> show(renderer.render("{{lj income fill filler}}",
    ...                      {'income': 3000, 'fill': 7, 'filler': '#'}))
    '3000###'
    >>> show(renderer.render("{{lj 'abc' 7}}", {}))
    'abc    '
    >>> show(renderer.render("{{+ a b}}", {'a': 1.2, 'b': 1.3}))
    '2.5'
    """
    _helpers = {}

    def register_helper(self, name, function):
        """ register a helper function for this renderer """
        self._helpers[name] = function

    def get_helper(self, fun):
        """ get registered helper 'fun' """
        return self._helpers[fun]

    def __init__(self, **kwargs):
        self._monkey = Handlebars()
        with self._monkey:
            super(Renderer, self).__init__(**kwargs)
            self._monkey(self)

    def render(self, template, *context, **kwargs):
        with self._monkey:
            return super(Renderer, self).render(template, *context, **kwargs)


class Handlebars(object):
    """ Handlebars helper for Renderer """
    def __init__(self):
        self._renderer = None
        self._original = None

    def __call__(self, renderer):
        self._renderer = renderer
        return self

    def context_get(self, stack, name):
        """ FIXME: doc """

        def cast_to_str(arg):
            """ try casting argument to str """
            try:
                return str(arg)
            except UnicodeEncodeError:
                return arg

        def unquote(arg):
            """ unquote argument """
            if arg == "''":
                return ''
            start, end = 0, None
            if arg[0] == "'" and arg[-1] == "'":
                start, end = 1, -1
            return cast_to_str(arg[start:end])

        def cast(arg):
            """ cast arguments passed to helper function """
            for caster in (int, decimal.Decimal, unquote):
                try:
                    return caster(arg)
                except UnicodeEncodeError:
                    pass
                except ValueError:
                    pass
                except decimal.InvalidOperation:
                    pass
            return arg

        args = name.split()
        if len(args) == 1:
            val = self._original(stack, name)
            return val

        fun, name, args = args[0], args[1], [cast(a) for a in args[2:]]
        fun = self._renderer.get_helper(fun)

        def resolve(arg):
            """ argument processing for function call """
            try:
                val = unquote(arg)
                if val == arg:
                    val = self._original(stack, arg)
            except (TypeError, KeyNotFoundError):
                val = arg
            return val

        val = resolve(name)
        args = [resolve(arg) for arg in args]
        val = fun(*[val]+args)
        return val

    def __enter__(self):
        """ patch pystache engine to support handlebars style helpers """
        assert self._original is None
        self._original = pystache.renderer.context_get
        pystache.renderer.context_get = self.context_get

    def __exit__(self, exc_type, exc_value, taceback):
        """ unpatch pystache engine after doing the job """
        assert self._original is not None
        pystache.renderer.context_get = self._original
        self._original = None
