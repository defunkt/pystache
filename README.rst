========
Pystache
========

.. image:: https://s3.amazonaws.com/webdev_bucket/pystache.png

Mustache_ is a framework-agnostic way to render logic-free views that is
inspired by ctemplate_ and et_.

As ctemplates says, "It emphasizes separating logic from presentation:
it is impossible to embed application logic in this template language."

Pystache is a Python implementation of Mustache. Pystache requires
Python 2.6.

Pystache is semantically versioned: http://semver.org.

Logo: David Phillips - http://davidphillips.us/

Documentation
=============

The `mustache(5)`_ man page is the main entry point for understanding
Mustache syntax.  Beyond this, the Mustache spec_ provides more complete
(and more current) documentation of Mustache's behavior.

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


Test It
=======

nose_ works great! ::

    pip install nose
    cd pystache
    nosetests

To include tests from the Mustache spec_ in your test runs: ::

    git submodule init
    git submodule update

To run all available tests (including doctests)::

    nosetests --with-doctest --doctest-extension=rst


Mailing List
==================

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
.. _et: http://www.ivan.fomichev.name/2008/05/erlang-template-engine-prototype.html
.. _Mustache: http://defunkt.github.com/mustache/
.. _mustache(5): http://mustache.github.com/mustache.5.html
.. _nose: http://somethingaboutorange.com/mrl/projects/nose/0.11.1/testing.html
.. _spec: https://github.com/mustache/spec
