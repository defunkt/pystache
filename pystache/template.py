import re
import cgi
import collections

modifiers = {}
def modifier(symbol):
    """Decorator for associating a function with a Mustache tag modifier.

    @modifier('P')
    def render_tongue(self, tag_name=None, context=None):
        return ":P %s" % tag_name

    {{P yo }} => :P yo
    """
    def set_modifier(func):
        modifiers[symbol] = func
        return func
    return set_modifier

class Template(object):
    
    tag_re = None
    
    otag = '{{'
    
    ctag = '}}'
    
    def __init__(self, template=None, context=None, **kwargs):
        from view import View
        
        self.template = template
        
        if kwargs:
            context.update(kwargs)
            
        self.view = context if isinstance(context, View) else View(context=context)
        
        self._compile_regexps()
    
    def _compile_regexps(self):
        tags = {
            'otag': re.escape(self.otag),
            'ctag': re.escape(self.ctag)
        }

        tag = r"%(otag)s(#|=|&|!|>|\{)?(.+?)\1?%(ctag)s+"
        self.tag_re = re.compile(tag % tags)
    
    def _render_sections(self, template, view):
        return template
    
    def _render_tags(self, template, view):
        while True:
            match = self.tag_re.search(template)
            if match is None:
                break
                
            tag, tag_type, tag_name = match.group(0, 1, 2)
            tag_name = tag_name.strip()
            func = modifiers[tag_type]
            replacement = func(self, tag_name, view)
            template = template.replace(tag, replacement)
        
        return template


    @modifier(None)
    def _render_tag(self, tag_name, view):
        raw = view.get(tag_name, '')
        
        return cgi.escape(unicode(raw))

    def render(self):
        template = self._render_sections(self.template, self.view)
        result = self._render_tags(template, self.view)
        
        return result