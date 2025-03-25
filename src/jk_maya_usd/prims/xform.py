from jk_maya_usd.prims.primbase import PrimBase

from pxr import Usd, UsdGeom, Vt
from maya import cmds

class Xform(PrimBase):
    def _export_impl(self, stage, dag_node, target):
        xform = UsdGeom.Xform.Define(stage, target)
        prim = xform.GetPrim() 
        return prim
        
    def _import_impl(self, stage, usd_prim, parent):
        short_name = usd_prim.GetName()
        if parent and cmds.objExists(parent):
            group = cmds.group(empty=True, name=short_name, parent=parent)
        else:
            group = cmds.group(empty=True, name=short_name)
        return group