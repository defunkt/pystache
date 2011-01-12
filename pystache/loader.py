import os

class Loader(object):
    
    template_extension = 'mustache'
    template_path = '.'
    template_encoding = None
    
    def load_template(self, template_name, template_dirs=None, encoding=None, extension=None):
        '''Returns the template string from a file or throws IOError if it non existent'''
        if None == template_dirs:
            template_dirs = self.template_path
        
        if encoding is not None:
            self.template_encoding = encoding
        
        if extension is not None:
            self.template_extension = extension
        
        file_name = template_name + '.' + self.template_extension

        # Given a single directory we'll load from it
        if isinstance(template_dirs, basestring):
            file_path = os.path.join(template_dirs, file_name)

            return self._load_template_file(file_path)
            
        # Given a list of directories we'll check each for our file
        for path in template_dirs:
            file_path = os.path.join(path, file_name)
            if os.path.exists(file_path):
                return self._load_template_file(file_path)
                
        raise IOError('"%s" not found in "%s"' % (template_name, ':'.join(template_dirs),))
    
    def _load_template_file(self, file_path):
        '''Loads and returns the template file from disk'''
        f = open(file_path, 'r')
        
        try:
            template = f.read()
            if self.template_encoding:
                template = unicode(template, self.template_encoding)
        finally:
            f.close()
        
        return template