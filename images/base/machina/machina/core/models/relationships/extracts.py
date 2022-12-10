from pyorient.ogm.property import String

from machina.core.models import Relationship

class Extracts(Relationship):
    """Establish a node (some binary data) as being
        extracted from another node"""
    label = 'extracts'
    # E.g. 'dynamic', 'static'
    method = String()