from enum import Enum

DEFAULT_CAMERAS = {'|back', '|bottom', '|front', '|persp', '|side', '|top'}
DESTINATION = "/Users/jakobkousholt/repos/jk_maya_usd/"
CALLBACK_ID_LONGNAME = "callbackId" 
CALLBACK_ID_SHORTNAME = "cbid"

ATTRIBUTE_PREFIX = "usd_"

COLORS = [(.9, .9, .9), (0.0, 1.0, 1.0), (1, 0.5, 1.0), (0.8, 0.2, 1.0)]


class USD_Type(Enum):
    XFORM = 'Xform'
    SCOPE = 'Scope'
    VARIANT = 'Variant'
    VARIANT_SET = 'VariantSet'

class USD_Purpose(Enum):
    PROXY = 'proxy'
    RENDER = 'render'
    INHERIT = 'inherit'
    DEFAULT = 'default'
    GUIDE = 'guide'
    NONE = ''

class USD_Kind(Enum):
    ASSEMBLY = 'assembly'
    COMPONENT = 'component'