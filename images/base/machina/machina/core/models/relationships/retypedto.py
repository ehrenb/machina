from pyorient.ogm.property import String

from machina.core.models import Relationship

class RetypedTo(Relationship):
    """Establish a node (some binary data) as being
        extracted from another node"""
    label = 'retype_to'
