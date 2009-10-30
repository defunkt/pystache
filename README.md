Pystache
========

Inspired by [ctemplate][1] and [et][2], Mustache is a
framework-agnostic way to render logic-free views.

As ctemplates says, "It emphasizes separating logic from presentation:
it is impossible to embed application logic in this template language."

Pystache is a Python implementation of Mustache. It has been tested
with Python 2.6.1.


Documentation
-------------

For now check out the [ctemplate][3] or [Mustache][4] docs.


Use It
------

    >>> import pystache
    >>> pystache.render('Hi {{person}}!', {'person': 'Mom'})
    'Hi Mom!'


Test It
-------

[nose][n] works great!

    easy_install nose
    cd pystache
    nosetests


Author
------

    context = { 'author': 'Chris Wanstrath', 'email': 'chris@ozmm.org' }
    pystache.render("{{author}} :: {{email}}", context)


[1]: http://code.google.com/p/google-ctemplate/
[2]: http://www.ivan.fomichev.name/2008/05/erlang-template-engine-prototype.html
[3]: http://google-ctemplate.googlecode.com/svn/trunk/doc/howto.html
[4]: http://github.com/defunkt/mustache#readme
[n]: http://somethingaboutorange.com/mrl/projects/nose/0.11.1/testing.html
