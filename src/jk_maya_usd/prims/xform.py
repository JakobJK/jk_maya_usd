from jk_maya_usd.prims.primbase import PrimBase

from pxr import Usd, UsdGeom, Vt
from maya.api import OpenMaya as om

class Xform(PrimBase):
    def _export_impl(self, stage, dag_node, target):
        # TODO: The fact maya groups has pivot points, and xforms don't will be fun.
        # We should still adhere to the common practice of zero out transformations.
        xform = UsdGeom.Xform.Define(stage, target)
        prim = xform.GetPrim() 
        return prim
    
    def _import_impl(self, stage, usd_prim):
        pass