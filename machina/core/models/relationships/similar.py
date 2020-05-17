from pyorient.ogm.property import Long, EmbeddedMap, String

from machina.core.models import Relationship

class Similar(Relationship):
    """Establish a node (some binary data) as being
        to another node"""
    label = 'similar'

    measurements = EmbeddedMap()