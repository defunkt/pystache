from pystache.template import Template

class Pystache(object):
    @staticmethod
    def render(template, context={}):
        return Template(template, context).render()
