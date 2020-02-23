from pyorient.ogm.property import String, Long, DateTime, EmbeddedMap

from machina.core.models import Node

class JPEG(Node):
    element_plural = 'jpegs'
    element_type = 'jpeg'

    # Common attributes
    md5 = String(nullable=False)
    sha256 = String(nullable=False)
    size = Long(nullable=False)
    ts = DateTime(nullable=False)
    type = String(nullable=False)

    # PNG attributes
    exif = EmbeddedMap()