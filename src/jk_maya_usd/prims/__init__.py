from jk_maya_usd.prims.mesh import Mesh
from jk_maya_usd.prims.xform import Xform
from jk_maya_usd.prims.nurbs_curve import NurbsCurve
from jk_maya_usd.prims.scope import Scope

usd_to_maya_prims = {
    'Xform': Xform,
    'Mesh': Mesh,
    'NurbsCurves': NurbsCurve,
    'Scope': Scope
}


maya_to_usd_prim = {
    'transform': Xform,
    'mesh': Mesh,
    'nurbsCurve': NurbsCurve,
}

usd_prims = { **usd_to_maya_prims, **maya_to_usd_prim }