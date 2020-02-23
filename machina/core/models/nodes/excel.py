from pyorient.ogm.property import String, Long, DateTime

from machina.core.models import Node

class Excel(Node):
    element_plural = 'excels'
    element_type = 'excel'

    # Common attributes
    md5 = String(nullable=False)
    sha256 = String(nullable=False)
    size = Long(nullable=False)
    ts = DateTime(nullable=False)
    type = String(nullable=False)