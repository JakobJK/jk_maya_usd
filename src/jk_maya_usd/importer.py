from maya import cmds
from pxr import Usd

from jk_maya_usd.constants import DESTINATION
from jk_maya_usd.prims import usd_prims
from jk_maya_usd.maya_utilities import create_variant_set, create_variant, create_group

class CustomUSDImporter():
    """ Import Scene from USD into Maya """
    def __init__(self):
        self.stage = None

    def _process_node(self, prim, parent):
        node_type = prim.GetTypeName()
        if node_type in usd_prims:
            cls = usd_prims[node_type](self) 
            maya_node = cls.import_node(self.stage, prim, parent)
            return maya_node
        else:
            print(f"{node_type} not in usd_prims")


    def _open_stage(self, file_path):
        self.stage = Usd.Stage.Open(file_path)
        if not self.stage:
            raise ValueError(f"Failed to open USD stage: {file_path}")


    def _traverse_prim(self, prim, parent):
        if not prim.IsValid():
            return
        dag_node = self._process_node(prim, parent)

        variant_sets = prim.GetVariantSets()
        variant_set_names = variant_sets.GetNames()

        for variant_set_name in variant_set_names:
            variant_set = variant_sets.GetVariantSet(variant_set_name)
            original_variant = variant_set.GetVariantSelection()

            for variant in variant_set.GetVariantNames():
                variant_set.SetVariantSelection(variant)
                print(f"  -> Traversing VariantSet '{variant_set_name}' with Variant '{variant}'")

                new_dag_node = self._add_variant(dag_node, variant_set.GetName(), variant)
                for child in prim.GetChildren():
                    self._traverse_prim(child, new_dag_node)

            variant_set.SetVariantSelection(original_variant)

        else:
            for child in prim.GetChildren():
                self._traverse_prim(child, dag_node)

        return dag_node

    def _add_variant(self, dag_node, variant_set, variant):
        if not cmds.objExists(f"{dag_node}|{variant_set}"):
            variant_set = create_variant_set(variant_set, parent=dag_node)
        else:
            variant_set = f"{dag_node}|{variant_set}"

        if not cmds.objExists(f"{variant_set}|{variant}"):
            variant = create_variant(variant, variant_set)

        return f"{variant_set}|{variant}"


    def import_from_usd(self, usd_file, top_dag_node: str = "", parent =None):
        self._open_stage(usd_file)
        self.temporary_dead_zone = create_group("temporary_dead_zone")

        dag_node = self._traverse_prim(self.stage.GetPseudoRoot(), parent)

        cmds.delete(self.temporary_dead_zone)
        
        return dag_node