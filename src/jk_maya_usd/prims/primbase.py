from abc import ABC, abstractmethod
from pxr import Usd
import maya.api.OpenMaya as om


class PrimBase(ABC):
    def __init__(self, processor):
        self.processor = processor

    def export_node(self, stage: Usd.Stage, dag_node: om.MObject, target: str) -> Usd.Prim:
        prim = self._export_impl(stage, dag_node, target)
        return prim

    @abstractmethod
    def _export_impl(self, stage: Usd.Stage, dag_node: om.MObject, target: str) -> Usd.Prim:
        pass

    def import_node(self, stage: Usd.Stage, dag_node: om.MObject, target: str) -> om.MObject:
        node = self._import_impl(stage, dag_node, target)
        return node

    @abstractmethod
    def _import_impl(self, stage: Usd.Stage, dag_node: om.MObject, target: str) -> om.MObject:
        pass

    def get_processor(self):
        return self.processor