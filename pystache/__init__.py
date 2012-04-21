# We keep all initialization code in a separate module.
# TODO: consider doing something like this instead:
#   from pystache.init import __version__, render, Renderer, TemplateSpec
from pystache.init import *

# TODO: make sure that "from pystache import *" exposes only the following:
#   ['__version__', 'render', 'Renderer', 'TemplateSpec']
#   and add a unit test for this.
