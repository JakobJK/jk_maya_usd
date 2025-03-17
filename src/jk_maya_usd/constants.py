from enum import Enum

DEFAULT_CAMERAS = {'|back', '|bottom', '|front', '|persp', '|side', '|top'}
DESTINATION = "/Users/jakobkousholt/repos/jk_maya_usd/output.usda"

class USD_Type(Enum):
    CLASS = 'Class'
    XFORM = 'Xform'
    SCOPE = 'Scope'
    VARIANT = 'Variant'
    VARIANT_SET = 'VariantSet'
    NONE = ''

class USD_Purpose(Enum):
    PROXY = 'proxy'
    RENDER = 'render'
    INHERIT = 'inherit'
    DEFAULT = 'default'
    NONE = ''

class USD_Kind(Enum):
    ASSEMBLY = 'assembly'
    COMPONENT = 'component'
