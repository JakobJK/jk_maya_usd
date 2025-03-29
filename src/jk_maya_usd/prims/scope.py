from pxr import Usd, UsdGeom, Vt
from maya import cmds

from jk_maya_usd.prims.primbase import PrimBase

from jk_maya_usd.maya_utilities import create_scope

class Scope(PrimBase):
    def _export_impl(self, stage, dag_node, target):
        scope = UsdGeom.Scope.Define(stage, target)
        return scope.GetPrim()
        
    def _import_impl(self, stage, usd_prim, parent):
        short_name = usd_prim.GetName()
        return create_scope(short_name, parent)