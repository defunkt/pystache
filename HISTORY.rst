History
=======

0.5.0 (TBD)
-----------

This version represents a major rewrite and refactoring of the code base
that also adds features and fixes many bugs.  All functionality and nearly
all unit tests have been preserved.  However, some backwards incompatible
changes to the API have been made.

Highlights:

* Pystache now passes all tests in version 1.0.3 of the `Mustache spec`_. [pvande]
* Removed View class: it is no longer necessary to subclass from View or
  from any other class to create a view.
* Replaced Template with Renderer class: template rendering behavior can be
  modified via the Renderer constructor or by setting attributes on a Renderer instance.
* Added TemplateSpec class: template rendering can be specified on a per-view
  basis by subclassing from TemplateSpec.
* Introduced separation of concerns and removed circular dependencies (e.g.
  between Template and View classes, cf. `issue #13`_).
* Unicode now used consistently throughout the rendering process.
* Expanded test coverage: nosetests now includes doctests and ~105 test cases
  from the Mustache spec (for a total of ~315 unit tests up from 56).
* Added rudimentary benchmarking script.

TODO: complete the list of key changes.

Features:

* Views and Renderers accept a custom template loader.  Also, this loader
  can be a dictionary of partials. [cjerdonek]
* Added a command-line interface. [vrde, cjerdonek]
* Custom escape function can now be passed to Template constructor. [cjerdonek]
* Template class can now handle non-ascii characters in non-unicode strings.
  Added default_encoding and decode_errors to Template constructor arguments.
  [cjerdonek]
* Loader supports a decode_errors argument. [cjerdonek]

API changes:

* Removed output_encoding options. [cjerdonek]
* Removed automatic use of markupsafe, if available. [cjerdonek]

Bug fixes:

* Context values no longer processed as template strings. [jakearchibald]
* Passing ``**kwargs`` to ``Template()`` modified the context. [cjerdonek]
* Passing ``**kwargs`` to ``Template()`` with no context raised an exception. [cjerdonek]
* Whitespace surrounding sections is no longer altered, in accordance with
  the mustache spec. [heliodor]
* Fixed an issue that affected the rendering of zeroes when using certain
  implementations of Python (i.e. PyPy). [alex]
* Extensionless template files could not be loaded. [cjerdonek]
* Multline comments now permitted. [fczuardi]

Misc:

* Added some docstrings. [kennethreitz]

0.4.1 (2012-03-25)
------------------
* Added support for Python 2.4. [wangtz, jvantuyl]

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


.. _issue #13: https://github.com/defunkt/pystache/issues/13
.. _Mustache spec: https://github.com/mustache/spec
