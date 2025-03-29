from maya import cmds
from pxr import Usd, UsdGeom

import os

from jk_maya_usd.constants import DEFAULT_CAMERAS
from jk_maya_usd.prims import usd_prims

from jk_maya_usd.maya_utilities import get_scene_scale, get_up_axis, get_node_type

class CustomUSDExporter():
    """ Export Scene from Maya to USD """
    def __init__(self):
        self.materials = {}

    def get_materials(self):
        return self.materials
    
    def _process_node(self, dag_node, node_type, target):
        if node_type in usd_prims:
            cls = usd_prims[node_type](self)
            prim = cls.export_node(self.stage, dag_node, target)
            print(f"Prim({prim.GetTypeName()}) created: {prim.GetName()}")
        else:
            print(f"{node_type} not processed")
            
    def _create_stage(self, stage_path):
        if os.path.exists(stage_path):
            os.remove(stage_path)


        # Create new stage
        self.stage = Usd.Stage.CreateNew(stage_path)

        up_axis = get_up_axis()
        meters_per_unit = get_scene_scale()
        up_axis_token = UsdGeom.Tokens.y if up_axis == 'Y' else UsdGeom.Tokens.z

        UsdGeom.SetStageUpAxis(self.stage, up_axis_token)
        UsdGeom.SetStageMetersPerUnit(self.stage, meters_per_unit)

    def _traverse(self, node, parent_path):
        node_type = get_node_type(node)
        short_name = node.split('|')[-1]
        target_path = f"{parent_path}/{short_name}"

        if node_type == "VariantSet":
            parent_prim = self.stage.GetPrimAtPath(parent_path)
            if not parent_prim.IsValid():
                return

            variant_set = parent_prim.GetVariantSets().AddVariantSet(short_name)
            children = cmds.listRelatives(node, children=True, fullPath=True) or []

            for child in children:
                variant_name = child.split('|')[-1]
                variant_set.AddVariant(variant_name)

                with variant_set.GetVariantEditContext(variant_name):
                    grandchildren = cmds.listRelatives(child, children=True, fullPath=True) or []
                    for grandchild in grandchildren:
                        self._traverse(grandchild, parent_path)

            if children:
                variant_set.SetVariantSelection(children[0].split('|')[-1])
            return

        self._process_node(node, node_type, target_path)


        if node_type in {'transform', 'Xform', 'Scope'}:
            children = cmds.listRelatives(node, children=True, fullPath=True) or []
            for child in children:
                self._traverse(child, target_path)

    def export_to_usd(self, stage_file_name, top_dag_node: str = ""):
        self._create_stage(stage_file_name)

        if top_dag_node:
            dag_nodes = cmds.listRelatives(top_dag_node, children=True, type="transform", fullPath=True) or []
        else:
            dag_nodes = [
                node for node in cmds.ls(type="transform", long=True)
                if not cmds.listRelatives(node, parent=True)
                and node not in DEFAULT_CAMERAS
            ]

        for node in dag_nodes:
            self._traverse(node, "")

        self.stage.GetRootLayer().Save()
        self.stage = None