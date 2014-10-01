# coding: utf-8

"""
This module provides command-line access to pystache.

Run this script using the -h option for command-line help.

"""


try:
    import json
except:
    # The json module is new in Python 2.6, whereas simplejson is
    # compatible with earlier versions.
    try:
        import simplejson as json
    except ImportError:
        # Raise an error with a type different from ImportError as a hack around
        # this issue:
        #   http://bugs.python.org/issue7559
        from sys import exc_info
        ex_type, ex_value, tb = exc_info()
        new_ex = Exception("%s: %s" % (ex_type.__name__, ex_value))
        raise new_ex.__class__, new_ex, tb

# The optparse module is deprecated in Python 2.7 in favor of argparse.
# However, argparse is not available in Python 2.6 and earlier.
from optparse import OptionParser
import sys, os
import csv

# We use absolute imports here to allow use of this script from its
# location in source control (e.g. for development purposes).
# Otherwise, the following error occurs:
#
#   ValueError: Attempted relative import in non-package
#
from pystache.common import TemplateNotFoundError
from pystache.renderer import Renderer


USAGE = """\
%prog [options] template context

Render a mustache template with the given context.

positional arguments:
  template    A filename or template string.
  context     A JSON string, or a JSON or CSV filename."""


def parse_args(sys_argv, usage):
    """
    Return an OptionParser for the script.

    """
    args = sys_argv[1:]

    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--format", dest="format",
                  help="format of the context string of filename (choose from: 'json', 'csv'). Default is JSON, unless context is a filename with .csv extension.",
                  choices=("json","csv"))
    parser.add_option("-m", "--multiple", dest="multiple",
                  help="""render the template for each context children,
writing output to KEY file (with no warning if file already exists).
If KEY is not a key of context children, then it is used as file output name,
and suffixed with a 3 digit incremental counter.""", metavar="KEY")
    options, args = parser.parse_args(args)

    try:
        template, context = args
    except ValueError as e:
        print('ERROR: %s\n' % e)
        parser.print_help()
        exit(1)
    except UnboundLocalError as e:
        print('ERROR: %s' % e)
        exit(1)

    return template, context, options.format, options.multiple


# TODO: verify whether the setup() method's entry_points argument
# supports passing arguments to main:
#
#     http://packages.python.org/distribute/setuptools.html#automatic-script-creation
#
def main(sys_argv=sys.argv):
    template, context, c_format, multiple = parse_args(sys_argv, USAGE)

    if template.endswith('.mustache'):
        template = template[:-9]

    renderer = Renderer()

    try:
        template = renderer.load_template(template)
    except TemplateNotFoundError:
        pass

    if context.endswith(".csv") or (c_format and (c_format == "csv")):
        try:
            context = csv.DictReader(open(context, 'rb'))#, delimiter=',', quotechar='"')
        except IOError:
            print('ERROR: Could not parse context as CSV file. Check usage for input format options')
            exit(-1)            
    else:
        try:
            context = json.load(open(context))
        except IOError:
            context = json.loads(context)
        except ValueError: #likely a not well-formed JSON string, or user forgot -f csv.
            print('ERROR: Could not parse context as JSON file or text, check usage for input format options')
            exit(1)

    if (multiple):
        print ("multiple render on field %s" % multiple)
        fileName, fileExt = os.path.splitext(multiple)
        for i,c in enumerate(context):
            if multiple in c:
                f_name = str(c[multiple])
            else:                
                f_name = "%s-%03d%s" % (fileName, i, fileExt)
            with open(f_name, "w") as f: # mode "wx" could be used to prevent overwriting, + pass IOError, adding "--force" option to override.
                rendered = renderer.render(template, c)
                f.write(rendered)
                print ("%s done") % f_name
    else:
        rendered = renderer.render(template, context)
        print rendered

if __name__=='__main__':
    main()
