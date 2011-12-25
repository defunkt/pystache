History
=======

Next Release (version TBD)
--------------------------

Features:

* Views and Renderers accept a custom template loader.  Also, this loader
  can be a dictionary of partials. [cjerdonek]
* Added a command-line interface. [vrde, cjerdonek]
* Markupsafe can now be disabled after import. [cjerdonek]
* Custom escape function can now be passed to Template constructor. [cjerdonek]
* Template class can now handle non-ascii characters in non-unicode strings.
  Added default_encoding and decode_errors to Template constructor arguments.
  [cjerdonek]
* Loader supports a decode_errors argument. [cjerdonek]

API changes:

* Template class replaced by a Renderer class. [cjerdonek]
* ``Loader.load_template()`` changed to ``Loader.get()``. [cjerdonek]
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
