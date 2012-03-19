from pystache import CustomizedTemplate

class Comments(CustomizedTemplate):
    template_path = 'examples'

    def title(self):
        return "A Comedy of Errors"
