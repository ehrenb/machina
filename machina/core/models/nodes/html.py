from pyorient.ogm.property import String, Long, DateTime

from machina.core.models import Node

class HTML(Node):
    element_plural = 'htmls'
    element_type = 'html'

    # Common attributes
    md5 = String(nullable=False)
    sha256 = String(nullable=False)
    size = Long(nullable=False)
    ts = DateTime(nullable=False)
    type = String(nullable=False)