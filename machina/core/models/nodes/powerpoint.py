from pyorient.ogm.property import String, Long, DateTime

from machina.core.models import Node

class Powerpoint(Node):
    element_plural = 'powerpoints'
    element_type = 'powerpoint'

    # Common attributes
    md5 = String(nullable=False)
    sha256 = String(nullable=False)
    size = Long(nullable=False)
    ts = DateTime(nullable=False)
    type = String(nullable=False)