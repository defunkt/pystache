Pystache
========

.. figure:: https://s3.amazonaws.com/webdev_bucket/pystache.png
   :align: center
   :alt: image

   image
`Pystache <https://github.com/defunkt/pystache>`_ is a Python
implementation of `Mustache <http://mustache.github.com/>`_. Mustache is
a framework-agnostic, logic-free templating system inspired by
`ctemplate <http://code.google.com/p/google-ctemplate/>`_ and
`et <http://www.ivan.fomichev.name/2008/05/erlang-template-engine-prototype.html>`_.
Like ctemplate, Mustache "emphasizes separating logic from presentation:
it is impossible to embed application logic in this template language."

The `mustache(5) <http://mustache.github.com/mustache.5.html>`_ man page
provides a good introduction to Mustache's syntax. For a more complete
(and more current) description of Mustache's behavior, see the official
`Mustache spec <https://github.com/mustache/spec>`_.

Pystache is `semantically versioned <http://semver.org>`_ and can be
found on `PyPI <http://pypi.python.org/pypi/pystache>`_. This version of
Pystache passes all tests in `version
1.1.2 <https://github.com/mustache/spec/tree/v1.1.2>`_ of the spec.

Logo: `David Phillips <http://davidphillips.us/>`_

Requirements
------------

Pystache is tested with--

-  Python 2.4 (requires simplejson `version
   2.0.9 <http://pypi.python.org/pypi/simplejson/2.0.9>`_ or earlier)
-  Python 2.5 (requires
   `simplejson <http://pypi.python.org/pypi/simplejson/>`_)
-  Python 2.6
-  Python 2.7
-  Python 3.1
-  Python 3.2

JSON support is needed only for the command-line interface and to run
the spec tests. We require simplejson for earlier versions of Python
since Python's `json <http://docs.python.org/library/json.html>`_ module
was added in Python 2.6.

For Python 2.4 we require an earlier version of simplejson since
simplejson stopped officially supporting Python 2.4 in simplejson
version 2.1.0. Earlier versions of simplejson can be installed manually,
as follows:

::

    pip install 'simplejson<2.1.0'

Install It
----------

::

    pip install pystache
    pystache-test

To install and test from source (e.g. from GitHub), see the Develop
section.

Use It
------

::

    >>> import pystache
    >>> print pystache.render('Hi {{person}}!', {'person': 'Mom'})
    Hi Mom!

You can also create dedicated view classes to hold your view logic.

Here's your view class (in .../examples/readme.py):

::

    class SayHello(object):
        def to(self):
            return "Pizza"

Instantiating like so:

::

    >>> from pystache.tests.examples.readme import SayHello
    >>> hello = SayHello()

Then your template, say\_hello.mustache (by default in the same
directory as your class definition):

::

    Hello, {{to}}!

Pull it together:

::

    >>> renderer = pystache.Renderer()
    >>> print renderer.render(hello)
    Hello, Pizza!

For greater control over rendering (e.g. to specify a custom template
directory), use the ``Renderer`` class like above. One can pass
attributes to the Renderer class constructor or set them on a Renderer
instance. To customize template loading on a per-view basis, subclass
``TemplateSpec``. See the docstrings of the
`Renderer <https://github.com/defunkt/pystache/blob/master/pystache/renderer.py>`_
class and
`TemplateSpec <https://github.com/defunkt/pystache/blob/master/pystache/template_spec.py>`_
class for more information.

You can also pre-parse a template:

::

    >>> parsed = pystache.parse(u"Hey {{#who}}{{.}}!{{/who}}")
    >>> print parsed
    [u'Hey ', _SectionNode(key=u'who', index_begin=12, index_end=18, parsed=[_EscapeNode(key=u'.'), u'!'])]

And then:

::

    >>> print renderer.render(parsed, {'who': 'Pops'})
    Hey Pops!
    >>> print renderer.render(parsed, {'who': 'you'})
    Hey you!

Python 3
--------

Pystache has supported Python 3 since version 0.5.1. Pystache behaves
slightly differently between Python 2 and 3, as follows:

-  In Python 2, the default html-escape function ``cgi.escape()`` does
   not escape single quotes; whereas in Python 3, the default escape
   function ``html.escape()`` does escape single quotes.
-  In both Python 2 and 3, the string and file encodings default to
   ``sys.getdefaultencoding()``. However, this function can return
   different values under Python 2 and 3, even when run from the same
   system. Check your own system for the behavior on your system, or do
   not rely on the defaults by passing in the encodings explicitly (e.g.
   to the ``Renderer`` class).

Unicode
-------

This section describes how Pystache handles unicode, strings, and
encodings.

Internally, Pystache uses `only unicode
strings <http://docs.python.org/howto/unicode.html#tips-for-writing-unicode-aware-programs>`_
(``str`` in Python 3 and ``unicode`` in Python 2). For input, Pystache
accepts both unicode strings and byte strings (``bytes`` in Python 3 and
``str`` in Python 2). For output, Pystache's template rendering methods
return only unicode.

Pystache's ``Renderer`` class supports a number of attributes to control
how Pystache converts byte strings to unicode on input. These include
the ``file_encoding``, ``string_encoding``, and ``decode_errors``
attributes.

The ``file_encoding`` attribute is the encoding the renderer uses to
convert to unicode any files read from the file system. Similarly,
``string_encoding`` is the encoding the renderer uses to convert any
other byte strings encountered during the rendering process into unicode
(e.g. context values that are encoded byte strings).

The ``decode_errors`` attribute is what the renderer passes as the
``errors`` argument to Python's built-in unicode-decoding function
(``str()`` in Python 3 and ``unicode()`` in Python 2). The valid values
for this argument are ``strict``, ``ignore``, and ``replace``.

Each of these attributes can be set via the ``Renderer`` class's
constructor using a keyword argument of the same name. See the Renderer
class's docstrings for further details. In addition, the
``file_encoding`` attribute can be controlled on a per-view basis by
subclassing the ``TemplateSpec`` class. When not specified explicitly,
these attributes default to values set in Pystache's ``defaults``
module.

Develop
-------

To test from a source distribution (without installing)--

::

    python test_pystache.py

To test Pystache with multiple versions of Python (with a single
command!), you can use `tox <http://pypi.python.org/pypi/tox>`_:

::

    pip install tox
    tox

If you do not have all Python versions listed in ``tox.ini``--

::

    tox -e py26,py32  # for example

The source distribution tests also include doctests and tests from the
Mustache spec. To include tests from the Mustache spec in your test
runs:

::

    git submodule init
    git submodule update

The test harness parses the spec's (more human-readable) yaml files if
`PyYAML <http://pypi.python.org/pypi/PyYAML>`_ is present. Otherwise, it
parses the json files. To install PyYAML--

::

    pip install pyyaml

To run a subset of the tests, you can use
`nose <http://somethingaboutorange.com/mrl/projects/nose/0.11.1/testing.html>`_:

::

    pip install nose
    nosetests --tests pystache/tests/test_context.py:GetValueTests.test_dictionary__key_present

**Running Pystache from source with Python 3.** Pystache is written in
Python 2 and must be converted with
`2to3 <http://docs.python.org/library/2to3.html>`_ prior to running
under Python 3. The installation process (and tox) do this conversion
automatically.

To ``import pystache`` from a source distribution while using Python 3,
be sure that you are importing from a directory containing a converted
version (e.g. from your site-packages directory after manually
installing) and not from the original source directory. Otherwise, you
will get a syntax error. You can help ensure this by not running the
Python IDE from the project directory when importing Pystache.

Mailing List
------------

There is a `mailing list <http://librelist.com/browser/pystache/>`_.
Note that there is a bit of a delay between posting a message and seeing
it appear in the mailing list archive.

Authors
-------

::

    >>> context = { 'author': 'Chris Wanstrath', 'maintainer': 'Chris Jerdonek' }
    >>> print pystache.render("Author: {{author}}\nMaintainer: {{maintainer}}", context)
    Author: Chris Wanstrath
    Maintainer: Chris Jerdonek

