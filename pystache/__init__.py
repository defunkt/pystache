from pystache.template import Template

def render(template, context={}):
    return Template(template, context).render()
