import re
import cgi
import collections
import os

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
            
            # Callable
            if it and isinstance(it, collections.Callable):
                replacer = it(inner)
            # Dictionary
            elif it and hasattr(it, 'keys') and hasattr(it, '__getitem__'):
                if section[2] != '^':
                    replacer = self._render_dictionary(inner, it)
            # Lists
            elif it and hasattr(it, '__iter__'):
                if section[2] != '^':
                    replacer = self._render_list(inner, it)            
            # Falsey and Negated or Truthy and Not Negated
            elif (not it and section[2] == '^') or (it and section[2] != '^'):
                replacer = inner
            
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
            view.template_path = self.view.template_path
            view.template_encoding = self.view.template_encoding
            view.parent = self.view
            insides.append(Template(template, view).render())
            
        return ''.join(insides)
    
    @modifier(None)
    def _render_tag(self, tag_name, view):
        raw = view.get(tag_name, '')
        
        # For methods with no return value
        if not raw and raw is not 0:
            return ''
        
        return cgi.escape(unicode(raw))
    
    @modifier('!')
    def _render_comment(self, tag_name, view):
        return ''
    
    @modifier('>')
    def _render_partial(self, template_name, view):
        from pystache import Loader
        template = Loader().load_template(template_name, view.template_path, encoding=view.template_encoding)

        return Template(template, view).render()

    @modifier('=')
    def _change_delimiter(self, tag_name, view):
        """Changes the Mustache delimiter."""
        self.otag, self.ctag = tag_name.split(' ')
        self._compile_regexps()
        return ''
    
    @modifier('{')
    @modifier('&')
    def render_unescaped(self, tag_name, view):
        """Render a tag without escaping it."""
        return unicode(view.get(tag_name, ''))
    
    def render(self, encoding=None):
        template = self._render_sections(self.template, self.view)
        result = self._render_tags(template, self.view)
        
        if encoding is not None:
            result = result.encode(encoding)
        
        return result