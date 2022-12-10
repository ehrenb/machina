from pyorient.ogm.property import String, Long, DateTime, EmbeddedSet, EmbeddedMap

from machina.core.models import Node

class APK(Node):
    element_plural = 'apks'
    element_type = 'apk'

    # APK Attribute
    package = String()
    name = String()
    androidversion_code = String()
    androidversion_name = String()
    permissions = EmbeddedSet(linked_to=String())
    activities = EmbeddedSet(linked_to=String())
    providers = EmbeddedSet(linked_to=String())
    receivers = EmbeddedSet(linked_to=String())
    services = EmbeddedSet(linked_to=String())
    min_sdk_version = String()
    max_sdk_version = String()
    max_sdk_version = String()
    effective_target_sdk_version = String()
    libraries = EmbeddedSet(linked_to=String())
    main_activity = String()
    content_provider_uris = EmbeddedSet(linked_to=String())

    classes = EmbeddedSet(linked_to=EmbeddedMap())

    # Common attributes
    md5 = String(nullable=False)
    sha256 = String(nullable=False)
    size = Long(nullable=False)
    ts = DateTime(nullable=False)
    type = String(nullable=False)
    ssdeep = String(nullable=True)