Pystache
========

<!-- Since PyPI rejects reST long descriptions that contain HTML, -->
<!-- HTML comments must be removed when converting this file to reST. -->
<!-- For more information on PyPI's behavior in this regard, see: -->
<!-- http://docs.python.org/distutils/uploading.html#pypi-package-display -->
<!-- The Pystache setup script strips 1-line HTML comments prior -->
<!-- to converting to reST, so all HTML comments should be one line. -->
<!-- -->
<!-- We leave the leading brackets empty here.  Otherwise, unwanted -->
<!-- caption text shows up in the reST version converted by pandoc. -->
[![ci](https://github.com/sarnold/pystache/actions/workflows/ci.yml/badge.svg)](https://github.com/sarnold/pystache/actions/workflows/ci.yml)
[![Conda](https://github.com/sarnold/pystache/actions/workflows/conda.yml/badge.svg)](https://github.com/sarnold/pystache/actions/workflows/conda.yml)
[![Wheels](https://github.com/sarnold/pystache/actions/workflows/wheels.yml/badge.svg)](https://github.com/sarnold/pystache/actions/workflows/wheels.yml)
[![Release](https://github.com/sarnold/pystache/actions/workflows/release.yml/badge.svg)](https://github.com/sarnold/pystache/actions/workflows/release.yml)
[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)

[![Latest release](https://img.shields.io/github/v/release/sarnold/pystache?include_prereleases)](https://github.com/sarnold/pystache/releases/latest)
[![License](https://img.shields.io/github/license/sarnold/pystache)](https://github.com/sarnold/pystache/blob/master/LICENSE)
[![Maintainability](https://api.codeclimate.com/v1/badges/a8fa1bf4638bfc6581b6/maintainability)](https://codeclimate.com/github/sarnold/pystache/maintainability)
[![codecov](https://codecov.io/gh/sarnold/pystache/branch/master/graph/badge.svg?token=5PZNMZBI6K)](https://codecov.io/gh/sarnold/pystache)



This updated fork of Pystache is currently tested on Python 3.6+ and in
Conda, on Linux, Macos, and Windows (Python 2.7 support has been removed).

![](gh/images/logo_phillips_small.png "mustachioed, monocled snake by David Phillips")

[Pystache](http://sarnold.github.com/pystache) is a Python
implementation of [Mustache](http://mustache.github.com/). Mustache is a
framework-agnostic, logic-free templating system inspired by
[ctemplate](http://code.google.com/p/google-ctemplate/) and
[et](http://www.ivan.fomichev.name/2008/05/erlang-template-engine-prototype.html).
Like ctemplate, Mustache "emphasizes separating logic from presentation:
it is impossible to embed application logic in this template language."

The [mustache(5)](http://mustache.github.com/mustache.5.html) man page
provides a good introduction to Mustache's syntax. For a more complete
(and more current) description of Mustache's behavior, see the official
[Mustache spec](https://github.com/mustache/spec).

Pystache is [semantically versioned](http://semver.org) and older versions
can still be found on [PyPI](http://pypi.python.org/pypi/pystache). This
version of Pystache now passes all tests in [version
1.1.3](https://github.com/mustache/spec/tree/v1.1.3) of the spec.


Requirements
------------

Pystache is tested with--

-   Python 3.6
-   Python 3.7
-   Python 3.8
-   Python 3.9
-   Conda (py36-py39)

[Distribute](http://packages.python.org/distribute/) (the setuptools fork)
is no longer required over [setuptools](http://pypi.python.org/pypi/setuptools),
as the current packaging is now PEP517-compliant.

JSON support is needed only for the command-line interface and to run
the spec tests; PyYAML can still be used (see the Develop section).

Official support for Python 2 will end with Pystache version 0.6.0.

Install It
----------

    pip install -U pystache -f https://github.com/sarnold/pystache/releases/

And test it--

    pystache-test

To install and test from source (e.g. from GitHub), see the Develop
section.

Use It
------

    >>> import pystache
    >>> print(pystache.render('Hi {{person}}!', {'person': 'Mom'}))
    Hi Mom!

You can also create dedicated view classes to hold your view logic.

Here's your view class (in ../pystache/tests/examples/readme.py):

    class SayHello(object):
        def to(self):
            return "Pizza"

Instantiating like so:

    >>> from pystache.tests.examples.readme import SayHello
    >>> hello = SayHello()

Then your template, say\_hello.mustache (by default in the same
directory as your class definition):

    Hello, {{to}}!

Pull it together:

    >>> renderer = pystache.Renderer()
    >>> print(renderer.render(hello))
    Hello, Pizza!

For greater control over rendering (e.g. to specify a custom template
directory), use the `Renderer` class like above. One can pass attributes
to the Renderer class constructor or set them on a Renderer instance. To
customize template loading on a per-view basis, subclass `TemplateSpec`.
See the docstrings of the
[Renderer](https://github.com/sarnold/pystache/blob/master/pystache/renderer.py)
class and
[TemplateSpec](https://github.com/sarnold/pystache/blob/master/pystache/template_spec.py)
class for more information.

You can also pre-parse a template:

    >>> parsed = pystache.parse(u"Hey {{#who}}{{.}}!{{/who}}")
    >>> print(parsed)
    ['Hey ', _SectionNode(key='who', index_begin=12, index_end=18, parsed=[_EscapeNode(key='.'), '!'])]

And then:

    >>> print(renderer.render(parsed, {'who': 'Pops'}))
    Hey Pops!
    >>> print(renderer.render(parsed, {'who': 'you'}))
    Hey you!

Python 3
--------

Pystache has supported Python 3 since version 0.5.1. Pystache behaves
slightly differently between Python 2 and 3, as follows:

-   In Python 2, the default html-escape function `cgi.escape()` does
    not escape single quotes.  In Python 3, the default escape function
    `html.escape()` does escape single quotes.
-   In both Python 2 and 3, the string and file encodings default to
    `sys.getdefaultencoding()`. However, this function can return
    different values under Python 2 and 3, even when run from the same
    system. Check your own system for the behavior on your system, or do
    not rely on the defaults by passing in the encodings explicitly
    (e.g. to the `Renderer` class).

Unicode
-------

This section describes how Pystache handles unicode, strings, and
encodings.

Internally, Pystache uses [only unicode
strings](http://docs.python.org/howto/unicode.html#tips-for-writing-unicode-aware-programs)
(`str` in Python 3 and `unicode` in Python 2). For input, Pystache
accepts both unicode strings and byte strings (`bytes` in Python 3 and
`str` in Python 2). For output, Pystache's template rendering methods
return only unicode.

Pystache's `Renderer` class supports a number of attributes to control
how Pystache converts byte strings to unicode on input. These include
the `file_encoding`, `string_encoding`, and `decode_errors` attributes.

The `file_encoding` attribute is the encoding the renderer uses to
convert to unicode any files read from the file system. Similarly,
`string_encoding` is the encoding the renderer uses to convert any other
byte strings encountered during the rendering process into unicode (e.g.
context values that are encoded byte strings).

The `decode_errors` attribute is what the renderer passes as the
`errors` argument to Python's built-in unicode-decoding function
(`str()` in Python 3 and `unicode()` in Python 2). The valid values for
this argument are `strict`, `ignore`, and `replace`.

Each of these attributes can be set via the `Renderer` class's
constructor using a keyword argument of the same name. See the Renderer
class's docstrings for further details. In addition, the `file_encoding`
attribute can be controlled on a per-view basis by subclassing the
`TemplateSpec` class. When not specified explicitly, these attributes
default to values set in Pystache's `defaults` module.

Develop
-------

To test from a source distribution (without installing)--

    python test_pystache.py

To test Pystache with multiple versions of Python (with a single
command!) and different platforms, you can use [tox](http://pypi.python.org/pypi/tox):

    pip install tox
    tox -e setup

To run tests on multiple versions with coverage, run:

    tox -e py38-linux,py39-linux  # for example

(substitute your platform above, eg, macos or windows)

The source distribution tests also include doctests and tests from the
Mustache spec. To include tests from the Mustache spec in your test
runs:

    git submodule init
    git submodule update

The test harness parses the spec's (more human-readable) yaml files if
[PyYAML](http://pypi.python.org/pypi/PyYAML) is present. Otherwise, it
parses the json files. To install PyYAML--

    pip install pyyaml

Once the submodule is available, you can run the full test set with:

    tox -e setup . ext/spec/specs

To run a subset of the tests, you can use
[nose](http://somethingaboutorange.com/mrl/projects/nose/0.11.1/testing.html):

    pip install nose
    nosetests --tests pystache/tests/test_context.py:GetValueTests.test_dictionary__key_present


Mailing List (old)
------------------

There is(was) a [mailing list](http://librelist.com/browser/pystache/). Note
that there is a bit of a delay between posting a message and seeing it
appear in the mailing list archive.

Credits
-------

    >>> import pystache
    >>> context = { 'author': 'Chris Wanstrath', 'maintainer': 'Chris Jerdonek','refurbisher': 'Steve Arnold' }
    >>> print(pystache.render("Author: {{author}}\nMaintainer: {{maintainer}}\nRefurbisher: {{refurbisher}}", context))
    Author: Chris Wanstrath
    Maintainer: Chris Jerdonek
    Refurbisher: Steve Arnold

Pystache logo by [David Phillips](http://davidphillips.us/) is licensed
under a [Creative Commons Attribution-ShareAlike 3.0 Unported
License](http://creativecommons.org/licenses/by-sa/3.0/deed.en_US).
![](http://i.creativecommons.org/l/by-sa/3.0/88x31.png "Creative
Commons Attribution-ShareAlike 3.0 Unported License")
