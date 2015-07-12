# -*- coding -*- : utf-8

"""
This module provides command-line access to pystache.

Run this script using the -h option for command-line help.

"""
import sys
import yaml

# The optparse module is deprecated in Python 2.7 in favor of argparse.
# However, argparse is not available in Python 2.6 and earlier.
from optparse import OptionParser

# We use absolute imports here to allow use of this script from its
# location in source control (e.g. for development purposes).
# Otherwise, the following error occurs:
#
#   ValueError: Attempted relative import in non-package
#
from pystache.renderer import Renderer

USAGE = """\
%prog [-hv] template [context]

Render a mustache template with the given context.

positional arguments:

  template    A filename or template string.
  context     A yaml or json filename, or a json string

if context is omitted, pystache read a YAML frontmatter
as render context from standard input if not a tty.

"""

MARKER = '---\n'  # marker for yaml sections (see mustache)

def parse_args(sys_argv, usage):
    """
    Return an OptionParser for the script.

    """
    args = sys_argv[1:]

    parser = OptionParser(usage=usage)
    parser.add_option('-v', '--version', action="store_true",
                      dest="show_version", default=False,
                      help="show version and exit")
    parser.add_option('-y', action="store_true", dest="yaml", default=False,
                      help="accept yaml as context format")
    options, args = parser.parse_args(args)
    if options.show_version:
        import pystache
        print("pystache %s" % pystache.__version__)
        sys.exit(0)
    if len(args) == 1:
        template, context = args[0], None
    else:
        template, context = args

    if options.show_version:
        import pystache
        print("pystache %s" % pystache.__version__)
        sys.exit(0)

    if len(args) == 1:
        template, context = args[0], None
    else:
        template, context = args

    return template, context, options


# TODO: verify whether the setup() method's entry_points argument
# supports passing arguments to main:
#
#     http://packages.python.org/distribute/setuptools.html#automatic-script-creation
#
MARKER = '---\n'

def arg2text(arg):
    """ get text from comand line arg """
    import errno
    if not isinstance(arg, str):
        return arg.read().decode('utf-8')  # FIXME
    else:
        try:
            if sys.version_info[0] == 3:
                with open(arg, encoding='utf-8') as data:
                    return data.read()
            else:
                with open(arg, 'rb') as data:
                    return data.read().decode('utf-8')
        except IOError, err:
            if err.errno == errno.ENOENT:
                # not a file, assumming first arg is template literal
                return arg

def extract_context(content, greedy=False):
    if content.startswith(MARKER):
        end = content.find(MARKER, len(MARKER))
        frontmatter = content[len(MARKER):end]
        content = content[end+len(MARKER):]
        context = yaml.load(frontmatter)
    elif greedy:
        frontmatter = content
        content = None
        context = yaml.load(frontmatter)
    else:
        context = {}
    return context, content

def main(argv=None):
    if argv is None:
        argv = sys.argv

    template, context, options = parse_args(argv, USAGE)

    if context is None and not sys.stdin.isatty():
        user_context = yaml.load(sys.stdin)
    elif context:
        user_context = yaml.load(arg2text(context))
    else:
        user_context = {}

    # assuming first arg is a filename or template literal
    template = arg2text(template)
    template_context, template = extract_context(template)
    if template.startswith(MARKER):
        end = template.find(MARKER, len(MARKER))
        frontmatter = template[len(MARKER):end]
        template = template[end+len(MARKER):]
        template_context = yaml.load(frontmatter)
    else:
        template_context = {}

    template_context.update(user_context)
    renderer = Renderer()
    rendered = renderer.render(template, template_context)
    print(rendered)

if __name__ == '__main__':
    main()
