from pyorient.ogm.property import String, Long, DateTime

from machina.core.models import Node, Relationship

class Artifact(Node):
    """A generic artifact for unknown/unsupported types"""
    element_plural = 'artifacts'
    element_type = 'artifact'

    # Common attributes
    md5 = String(nullable=False)
    sha256 = String(nullable=False)
    size = Long(nullable=False)
    ts = DateTime(nullable=False)
    type = String(nullable=False)
    ssdeep = String(nullable=True)