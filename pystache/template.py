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

        section = r"%(otag)s[\#|^]([^\}]*)%(ctag)s\s*(.+?\s*)%(otag)s/\1%(ctag)s"
        self.section_re = re.compile(section % tags, re.M|re.S)

        tag = r"%(otag)s(#|=|&|!|>|\{)?(.+?)\1?%(ctag)s+"
        self.tag_re = re.compile(tag % tags)
    
    def _render_sections(self, template, view):
        while True:
            match = self.section_re.search(template)
            if match is None:
                break

            section, section_name, inner = match.group(0, 1, 2)
            section_name = section_name.strip()
            
            it = view.get(section_name, None)
            replacer = ''
            
            # Dictionary
            if it and hasattr(it, 'keys') and hasattr(it, '__getitem__'):
                if section[2] != '^':
                    replacer = self._render_dictionary(inner, it)
            elif it and hasattr(it, '__iter__'):
                if section[2] != '^':
                    replacer = self._render_list(inner, it)
            
            template = template.replace(section, replacer)
        
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

    def _render_dictionary(self, template, context):
        from view import View
        
        view = View(context=context)
        view.parent = self.view
        return Template(template, view).render()
    
    def _render_list(self, template, listing):
        from view import View
        
        insides = []
        for item in listing:
            view = View(context=item)
            view.parent = self.view
            insides.append(Template(template, view).render())
            
        return ''.join(insides)
    
    @modifier(None)
    def _render_tag(self, tag_name, view):
        raw = view.get(tag_name, '')
        
        return cgi.escape(unicode(raw))

    def render(self):
        template = self._render_sections(self.template, self.view)
        result = self._render_tags(template, self.view)
        
        return result