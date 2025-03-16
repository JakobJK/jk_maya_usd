from abc import ABC, abstractmethod


class PrimBase(ABC):
    def __init__(self):
        self.prim = None

    def export_node(self, stage: str, dag_node: str, target: str):
        prim = self._export_impl(stage, dag_node, target)
        self._attach_attributes_to_usd_nodes(stage, dag_node, target)
        return prim

    @abstractmethod
    def _export_impl(self, stage: str, dag_node: str, target: str):
        pass

    def import_prim(self, stage: str, dag_node: str, target: str):
        prim = self._import_impl(stage, dag_node, target)
        self._attach_attributes_to_maya_nodes(stage, dag_node, target)
        return prim
        
    @abstractmethod
    def _import_impl(self, stage: str, dag_node: str, target: str):
        pass

    def _attach_attributes_to_usd_nodes(self, stage, dag_node, target):
        pass

    def _attach_attributes_to_maya_nodes(self, stage, dag_node, target):
        pass