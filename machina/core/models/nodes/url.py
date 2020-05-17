from pyorient.ogm.property import String, Integer

from machina.core.models import Node

class URL(Node):
    element_plural = 'urls'
    element_type = 'url'

    # URL Attribute
    url = String()

    ssdeep = String(nullable=True)