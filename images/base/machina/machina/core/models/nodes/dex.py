from pyorient.ogm.property import String, Long, DateTime

from machina.core.models import Node

class Dex(Node):
    element_plural = 'dexs'
    element_type = 'dex'

    # Common attributes
    md5 = String(nullable=False)
    sha256 = String(nullable=False)
    size = Long(nullable=False)
    ts = DateTime(nullable=False)
    type = String(nullable=False)
    ssdeep = String(nullable=True)