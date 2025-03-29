from jk_maya_usd.prims.primbase import PrimBase

from pxr import UsdGeom
from maya import cmds

from jk_maya_usd.maya_utilities import create_group

class Xform(PrimBase):
    def _export_impl(self, stage, dag_node, target):
        xform = UsdGeom.Xform.Define(stage, target)
        xform_ops = UsdGeom.Xformable(xform)

        translate = cmds.getAttr(f"{dag_node}.translate")[0]
        rotate = cmds.getAttr(f"{dag_node}.rotate")[0]
        scale = cmds.getAttr(f"{dag_node}.scale")[0]

        xform_ops.AddTranslateOp().Set(translate)
        xform_ops.AddRotateXYZOp().Set(rotate)
        xform_ops.AddScaleOp().Set(scale)

        return xform.GetPrim()
        
    def _import_impl(self, stage, usd_prim, parent):
        short_name = usd_prim.GetName()

        xform = UsdGeom.Xform(usd_prim)
        xform_ops = xform.GetOrderedXformOps()

        translate = [0, 0, 0]
        rotate = [0, 0, 0]
        scale = [1, 1, 1]

        for op in xform_ops:
            op_type = op.GetOpType()
            value = op.Get()
            if op_type == UsdGeom.XformOp.TypeTranslate:
                translate = value
            elif op_type == UsdGeom.XformOp.TypeRotateXYZ:
                rotate = value
            elif op_type == UsdGeom.XformOp.TypeScale:
                scale = value

        group = create_group(short_name, parent)
        cmds.setAttr(group + ".translate", *translate)
        cmds.setAttr(group + ".rotate", *rotate)
        cmds.setAttr(group + ".scale", *scale)
        return group







