from jk_maya_usd.prims.primbase import PrimBase
from jk_maya_usd.maya_utilities import create_transform, get_mobject_from_name
from pxr import UsdGeom, Vt, Sdf
from maya.api import OpenMaya as om

class NurbsCurve(PrimBase):
    def _export_impl(self, stage, dag_node, target):
        curve = UsdGeom.NurbsCurves.Define(stage, target)
        prim = curve.GetPrim()

        selection_list = om.MSelectionList()
        selection_list.add(dag_node)
        dag_path = selection_list.getDagPath(0)
        curve_fn = om.MFnNurbsCurve(dag_path)

        points = curve_fn.cvPositions(om.MSpace.kWorld)
        curve.GetPointsAttr().Set(Vt.Vec3fArray([(p.x, p.y, p.z) for p in points]))
        curve.GetOrderAttr().Set(Vt.IntArray([curve_fn.degree + 1]))
        curve.GetCurveVertexCountsAttr().Set(Vt.IntArray([curve_fn.numCVs]))
        curve.GetKnotsAttr().Set(Vt.DoubleArray(curve_fn.knots()))

        return prim

    def _import_impl(self, stage, usd_prim, parent):
        if not usd_prim or not usd_prim.IsValid():
            return None

        curve = UsdGeom.NurbsCurves(usd_prim)
        points = curve.GetPointsAttr().Get() or []
        counts = curve.GetCurveVertexCountsAttr().Get() or []
        order = curve.GetOrderAttr().Get() or []
        knots = curve.GetKnotsAttr().Get() or []

        if not points or not counts or not order or not knots:
            return None

        mfloat_points = om.MPointArray([om.MPoint(*p) for p in points])
        knot_array = om.MDoubleArray(knots)
        degree = order[0] - 1
        parent_obj = get_mobject_from_name(parent)
        transform_name = usd_prim.GetName()
        transform_obj = create_transform(transform_name, parent_obj)

        curve_fn = om.MFnNurbsCurve()
        curve_obj = curve_fn.create(
            mfloat_points,
            knot_array,
            degree,
            om.MFnNurbsCurve.kOpen,
            False,
            False,
            transform_obj
        )

        dag_path = om.MDagPath.getAPathTo(curve_obj)
        return dag_path.fullPathName()