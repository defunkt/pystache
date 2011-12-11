from pystache import Template
import argparse
import json
from loader import Loader

def main():
    parser = argparse.ArgumentParser(description='Render a mustache template with the given context.')
    parser.add_argument('template',  help='A filename or a template code.')
    parser.add_argument('context', help='A filename or a JSON string')
    args = parser.parse_args()

    if args.template.endswith('.mustache'):
        args.template = args.template[:-9]

    try:
        template = Loader().load_template(args.template)
    except IOError:
        template = args.template

    try:
        context = json.load(open(args.context))
    except IOError:
        context = json.loads(args.context)

    print(Template(template, context).render())


if __name__=='__main__':
    main()

