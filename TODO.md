TODO
====

* Add Travis CI status image to README.
* Make sure the new README will parse succesfully in PyPI.  See also:
    * http://bugs.python.org/issue15231
    * https://github.com/cjerdonek/molt/commit/91a7f158fdd5b93b90201ae0c128d2bbbaf7f913#README.md
* Add a Renderer.render_name() method to render by template name.
* Turn the benchmarking script at pystache/tests/benchmark.py into a command in pystache/commands, or
  make it a subcommand of one of the existing commands (i.e. using a command argument).
* Provide support for logging in at least one of the commands.
* Make sure command parsing to pystache-test doesn't break with Python 2.4 and earlier.
* Combine pystache-test with the main command.
