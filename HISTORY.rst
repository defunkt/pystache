History
=======

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
