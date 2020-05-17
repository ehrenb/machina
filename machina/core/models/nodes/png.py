from pyorient.ogm.property import String, Long, DateTime, EmbeddedMap

from machina.core.models import Node

class PNG(Node):
    element_plural = 'pngs'
    element_type = 'png'

    # Common attributes
    md5 = String(nullable=False)
    sha256 = String(nullable=False)
    size = Long(nullable=False)
    ts = DateTime(nullable=False)
    type = String(nullable=False)
    ssdeep = String(nullable=True)

    # PNG attributes
    exif = EmbeddedMap()