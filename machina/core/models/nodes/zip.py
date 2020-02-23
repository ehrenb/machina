from pyorient.ogm.property import String, Long, DateTime

from machina.core.models import Node

class Zip(Node):
    element_plural = 'zips'
    element_type = 'zip'

    # Common attributes
    md5 = String(nullable=False)
    sha256 = String(nullable=False)
    size = Long(nullable=False)
    ts = DateTime(nullable=False)
    type = String(nullable=False)