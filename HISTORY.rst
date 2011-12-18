History
=======

Next Release (version TBD)
--------------------------
* API change: pass the context to render to Template.render() instead of
  Template.__init__(). [cjerdonek]
* Bugfix: Passing **kwargs to Template() modified the context. [cjerdonek]
* Bugfix: Passing **kwargs to Template() with no context raised an
  exception. [cjerdonek]
* Bugfix: Whitespace surrounding sections is no longer altered, in
  accordance with the mustache spec. [heliodor]
* A custom template loader can now be passed to a View. [cjerdonek]
* Added a command-line interface. [vrde, cjerdonek]
* Bugfix: Fixed an issue that affected the rendering of zeroes when using
  certain implementations of Python (i.e. PyPy). [alex]
* Added some docstrings. [kennethreitz]

0.4.0 (2011-01-12)
------------------
* Add support for nested contexts (within template and view)
* Add support for inverted lists
* Decoupled template loading

0.3.1 (2010-05-07)
------------------

* Fix package

0.3.0 (2010-05-03)
------------------

* View.template_path can now hold a list of path
* Add {{& blah}} as an alias for {{{ blah }}}
* Higher Order Sections
* Inverted sections

0.2.0 (2010-02-15)
------------------

* Bugfix: Methods returning False or None are not rendered
* Bugfix: Don't render an empty string when a tag's value is 0. [enaeseth]
* Add support for using non-callables as View attributes. [joshthecoder]
* Allow using View instances as attributes. [joshthecoder]
* Support for Unicode and non-ASCII-encoded bytestring output. [enaeseth]
* Template file encoding awareness. [enaeseth]

0.1.1 (2009-11-13)
------------------

* Ensure we're dealing with strings, always
* Tests can be run by executing the test file directly

0.1.0 (2009-11-12)
------------------

* First release
