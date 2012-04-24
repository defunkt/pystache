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

* Python 2.4 (requires simplejson `version 2.0.9`_ or earlier)
* Python 2.5 (requires simplejson_)
* Python 2.6
* Python 2.7
* Python 3.1
* Python 3.2

JSON support is needed only for the command-line interface and to run the
spec tests.  We require simplejson for earlier versions of Python since
Python's json_ module was added in Python 2.6.

For Python 2.4 we require an earlier version of simplejson since simplejson
stopped officially supporting Python 2.4 in simplejson version 2.1.0.
Earlier versions of simplejson can be installed manually, as follows: ::

    pip install 'simplejson<2.1.0'


Install It
==========

::

    pip install pystache


Use It
======

::

    >>> import pystache
    >>> print pystache.render('Hi {{person}}!', {'person': 'Mom'})
    Hi Mom!

You can also create dedicated view classes to hold your view logic.

Here's your view class (in examples/readme.py)::

    class SayHello(object):

        def to(self):
            return "Pizza"

Like so::

    >>> from pystache.tests.examples.readme import SayHello
    >>> hello = SayHello()

Then your template, say_hello.mustache (by default in the same directory)::

    Hello, {{to}}!

Pull it together::

    >>> renderer = pystache.Renderer()
    >>> print renderer.render(hello)
    Hello, Pizza!

For greater control over rendering (e.g. to specify a custom template directory),
use the ``Renderer`` class directly.  One can pass attributes to the class's
constructor or set them on an instance.
To customize template loading on a per-view basis, subclass ``TemplateSpec``.
See the docstrings of the Renderer_ class and TemplateSpec_ class for
more information.


Python 3
========

As of version 0.5.1, Pystache fully supports Python 3.  There are slight
differences in behavior between Pystache running under Python 2 and 3,
as follows:

* In Python 2, the default html-escape function ``cgi.escape()`` does not
  escape single quotes; whereas in Python 3, the default escape function
  ``html.escape()`` does escape single quotes.
* In both Python 2 and 3, the string and file encodings default to
  ``sys.getdefaultencoding()``.  However, this function can return different
  values under Python 2 and 3, even when run from the same system.  Check
  your own system for the behavior on your system, or do not rely on the
  defaults by passing in the encodings explicitly (e.g. to the ``Renderer`` class).


Unicode Handling
================

This section describes Pystache's handling of unicode (e.g. strings and
encodings).

Internally, Pystache uses `only unicode strings`_ (type ``str`` in Python 3 and
type ``unicode`` in Python 2).  For input, Pystache accepts both unicode strings
and byte strings (``bytes`` in Python 3 and ``str`` in Python 2).  For output,
Pystache's template rendering methods return only unicode.

Pystache's ``Renderer`` class supports a number of attributes to control how
Pystache converts byte strings to unicode on input.  These include the
``file_encoding``, ``string_encoding``, and ``decode_errors`` attributes.

The ``file_encoding`` attribute is the encoding the renderer uses to convert
to unicode any files read from the file system.  Similarly, ``string_encoding``
is the encoding the renderer uses to convert any other byte strings encountered
during the rendering process into unicode (e.g. context values that are
encoded byte strings).

The ``decode_errors`` attribute is what the renderer passes as the ``errors``
argument to Python's built-in unicode-decoding function (``str()`` in Python 3
and ``unicode()`` in Python 2).  The valid values for this argument are
``strict``, ``ignore``, and ``replace``.

Each of these attributes can be set via the ``Renderer`` class's constructor
using a keyword argument of the same name.  See the Renderer class's
docstrings for further details.  In addition, the ``file_encoding``
attribute can be controlled on a per-view basis by subclassing the
``TemplateSpec`` class.  When not specified explicitly, these attributes
default to values set in Pystache's ``defaults`` module.


Test It
=======

From an install-- ::

    pystache-test

From a source distribution-- ::

    python test_pystache.py

To test Pystache source under multiple versions of Python all at once, you
can use tox_: ::

    pip install tox
    tox

If you do not have all Python versions listed in ``tox.ini``-- ::

    tox -e py26,py27  # for example

The source distribution tests also include doctests and tests from the
Mustache spec.  To include tests from the Mustache spec in your test runs: ::

    git submodule init
    git submodule update

The test harness parses the spec's (more human-readable) yaml files if PyYAML_
is present.  Otherwise, it parses the json files.  To install PyYAML-- ::

    pip install pyyaml

To test Pystache from a source distribution with Python 3.x, you must use tox.
This is because the source code must first be run through 2to3_.


Mailing List
============

As of November 2011, there's a mailing list, pystache@librelist.com.

Archive: http://librelist.com/browser/pystache/

Note: There's a bit of a delay in seeing the latest emails appear
in the archive.


Author
======

::

    >>> context = { 'author': 'Chris Wanstrath', 'maintainer': 'Chris Jerdonek' }
    >>> print pystache.render("Author: {{author}}\nMaintainer: {{maintainer}}", context)
    Author: Chris Wanstrath
    Maintainer: Chris Jerdonek


.. _2to3: http://docs.python.org/library/2to3.html
.. _built-in unicode function: http://docs.python.org/library/functions.html#unicode
.. _ctemplate: http://code.google.com/p/google-ctemplate/
.. _David Phillips: http://davidphillips.us/
.. _Distribute: http://pypi.python.org/pypi/distribute
.. _et: http://www.ivan.fomichev.name/2008/05/erlang-template-engine-prototype.html
.. _json: http://docs.python.org/library/json.html
.. _Mustache: http://mustache.github.com/
.. _Mustache spec: https://github.com/mustache/spec
.. _mustache(5): http://mustache.github.com/mustache.5.html
.. _only unicode strings: http://docs.python.org/howto/unicode.html#tips-for-writing-unicode-aware-programs
.. _PyPI: http://pypi.python.org/pypi/pystache
.. _Pystache: https://github.com/defunkt/pystache
.. _PyYAML: http://pypi.python.org/pypi/PyYAML
.. _Renderer: https://github.com/defunkt/pystache/blob/master/pystache/renderer.py
.. _semantically versioned: http://semver.org
.. _simplejson: http://pypi.python.org/pypi/simplejson/
.. _TemplateSpec: https://github.com/defunkt/pystache/blob/master/pystache/template_spec.py
.. _test: http://packages.python.org/distribute/setuptools.html#test
.. _tox: http://pypi.python.org/pypi/tox
.. _version 1.0.3: https://github.com/mustache/spec/tree/48c933b0bb780875acbfd15816297e263c53d6f7
.. _version 2.0.9: http://pypi.python.org/pypi/simplejson/2.0.9
