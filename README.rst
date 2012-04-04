========
Pystache
========

.. image:: https://s3.amazonaws.com/webdev_bucket/pystache.png

Pystache_ is a Python implementation of Mustache_.
Mustache is a framework-agnostic, logic-free templating system inspired
by ctemplate_ and et_.  Like ctemplate, Mustache "emphasizes
separating logic from presentation: it is impossible to embed application
logic in this template language."

The `mustache(5)`_ man page provides a good introduction to Mustache's
syntax.  For a more complete (and more current) description of Mustache's
behavior, see the official `Mustache spec`_.

Pystache is `semantically versioned`_ and can be found on PyPI_.  This
version of Pystache passes all tests in `version 1.0.3`_ of the spec.

Logo: `David Phillips`_


Requirements
============

Pystache is tested with the following versions of Python:

* Python 2.4 (requires simplejson version 2.0.9 or earlier)
* Python 2.5 (requires simplejson)
* Python 2.6
* Python 2.7

JSON support is needed only for the command-line interface and to run the
spec tests.  Python's json_ module is new as of Python 2.6.  Python's
simplejson_ package works with earlier versions of Python.  Because
simplejson stopped officially supporting Python 2.4 as of version 2.1.0,
Python 2.4 requires an earlier version.


Install It
==========

::

    pip install pystache


Use It
======

::

    >>> import pystache
    >>> pystache.render('Hi {{person}}!', {'person': 'Mom'})
    u'Hi Mom!'

You can also create dedicated view classes to hold your view logic.

Here's your view class (in examples/readme.py)::

    class SayHello(object):

        def to(self):
            return "Pizza"

Like so::

    >>> from examples.readme import SayHello
    >>> hello = SayHello()

Then your template, say_hello.mustache::

    Hello, {{to}}!

Pull it together::

    >>> renderer = pystache.Renderer()
    >>> renderer.render(hello)
    u'Hello, Pizza!'


Unicode Handling
================

This section describes Pystache's handling of unicode (e.g. strings and
encodings).

Internally, Pystache uses `only unicode strings`_.  For input, Pystache accepts
both ``unicode`` and ``str`` strings.  For output, Pystache's template
rendering methods return only unicode.

Pystache's ``Renderer`` class supports a number of attributes that control how
Pystache converts ``str`` strings to unicode on input.  These include the
``file_encoding``, ``string_encoding``, and ``decode_errors`` attributes.

The ``file_encoding`` attribute is the encoding the renderer uses to convert
to unicode any files read from the file system.  Similarly, ``string_encoding``
is the encoding the renderer uses to convert to unicode any other strings of
type ``str`` encountered during the rendering process (e.g. context values
of type ``str``).

The ``decode_errors`` attribute is what the renderer passes as the ``errors``
argument to Python's `built-in unicode function`_ ``unicode()`` when
converting.  The valid values for this argument are ``strict``, ``ignore``,
and ``replace``.

Each of these attributes can be set via the ``Renderer`` class's constructor
using a keyword argument of the same name.  See the Renderer class's
docstrings for further details.  In addition, the ``file_encoding``
attribute can be controlled on a per-view basis by subclassing the
``TemplateSpec`` class.  When not specified explicitly, these attributes
default to values set in Pystache's ``defaults`` module.


Test It
=======

nose_ works great! ::

    pip install nose
    cd pystache
    nosetests

Depending on your Python version and nose installation, you may need
to type, for example ::

    nosetests-2.4

To include tests from the Mustache spec in your test runs: ::

    git submodule init
    git submodule update

To run all available tests (including doctests)::

    nosetests --with-doctest --doctest-extension=rst

or alternatively (using setup.cfg)::

    python setup.py nosetests

To run a subset of the tests, you can use this pattern, for example: ::

    nosetests --tests tests/test_context.py:GetValueTests.test_dictionary__key_present


Mailing List
============

As of November 2011, there's a mailing list, pystache@librelist.com.

Archive: http://librelist.com/browser/pystache/

Note: There's a bit of a delay in seeing the latest emails appear
in the archive.


Author
======

::

    >>> context = { 'author': 'Chris Wanstrath', 'email': 'chris@ozmm.org' }
    >>> pystache.render("{{author}} :: {{email}}", context)
    u'Chris Wanstrath :: chris@ozmm.org'


.. _ctemplate: http://code.google.com/p/google-ctemplate/
.. _David Phillips: http://davidphillips.us/
.. _et: http://www.ivan.fomichev.name/2008/05/erlang-template-engine-prototype.html
.. _json: http://docs.python.org/library/json.html
.. _Mustache: http://mustache.github.com/
.. _Mustache spec: https://github.com/mustache/spec
.. _mustache(5): http://mustache.github.com/mustache.5.html
.. _nose: http://somethingaboutorange.com/mrl/projects/nose/0.11.1/testing.html
.. _only unicode strings: http://docs.python.org/howto/unicode.html#tips-for-writing-unicode-aware-programs
.. _PyPI: http://pypi.python.org/pypi/pystache
.. _Pystache: https://github.com/defunkt/pystache
.. _semantically versioned: http://semver.org
.. _simplejson: http://pypi.python.org/pypi/simplejson/
.. _built-in unicode function: http://docs.python.org/library/functions.html#unicode
.. _version 1.0.3: https://github.com/mustache/spec/tree/48c933b0bb780875acbfd15816297e263c53d6f7
