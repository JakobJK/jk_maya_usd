from jk_maya_usd.prims.mesh import Mesh
from jk_maya_usd.prims.xform import Xform
from jk_maya_usd.prims.nurbs_curve import NurbsCurve
from jk_maya_usd.prims.scope import Scope

usd_prims = {
    'transform': Xform,
    'xform': Xform,
    'mesh': Mesh,
    'nurbsCurve': NurbsCurve,
    'nurbscurves': NurbsCurve,
    'scope': Scope
}
