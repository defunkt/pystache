========
Pystache
========

.. image:: https://s3.amazonaws.com/webdev_bucket/pystache.png

Inspired by ctemplate_ and et_, Mustache_ is a
framework-agnostic way to render logic-free views.

As ctemplates says, "It emphasizes separating logic from presentation:
it is impossible to embed application logic in this template language."

Pystache is a Python implementation of Mustache. Pystache requires
Python 2.4.

Pystache is semantically versioned: http://semver.org.

Logo: David Phillips - http://davidphillips.us/ 

Documentation
=============

The different Mustache tags are documented at `mustache(5)`_.

Install It
==========

::

    pip install pystache


Use It
======

::

    >>> import pystache
    >>> pystache.render('Hi {{person}}!', {'person': 'Mom'})
    'Hi Mom!'

You can also create dedicated view classes to hold your view logic.

Here's your simple.py::

    import pystache
    class Simple(pystache.View):
        def thing(self):
            return "pizza"

Then your template, simple.mustache::

    Hi {{thing}}!

Pull it together::

    >>> Simple().render()
    'Hi pizza!'


Test It
=======

nose_ works great! ::

    pip install nose
    cd pystache
    nosetests


Mailing List
==================
As of Nov 26, 2011, there's a mailing list, pystache@librelist.com.

Archive: http://librelist.com/browser/pystache/

Note: There's a bit of a delay in seeing the latest emails appear
in the archive.

Author
======

::

    context = { 'author': 'Chris Wanstrath', 'email': 'chris@ozmm.org' }
    pystache.render("{{author}} :: {{email}}", context)


.. _ctemplate: http://code.google.com/p/google-ctemplate/
.. _et: http://www.ivan.fomichev.name/2008/05/erlang-template-engine-prototype.html
.. _Mustache: http://defunkt.github.com/mustache/
.. _mustache(5): http://mustache.github.com/mustache.5.html
.. _nose: http://somethingaboutorange.com/mrl/projects/nose/0.11.1/testing.html
