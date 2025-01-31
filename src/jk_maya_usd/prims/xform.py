from jk_maya_usd.prims.primbase import PrimBase

from pxr import Usd, UsdGeom, Vt
from maya.api import OpenMaya as om

class Xform(PrimBase):
    def export_node(self, stage, dag_node, target):
        # TODO: The fact maya groups has pivot points, and xforms don't will be fun.
        xform = UsdGeom.Xform.Define(stage, target)
        prim = xform.GetPrim() 
        return prim
    
    def import_prim(self, stage, usd_prim):
        pass