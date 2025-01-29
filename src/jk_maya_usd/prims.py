from abc import ABC, abstractmethod



class PrimBase(ABC):
    @abstractmethod
    def export_node(self, dag_node):
        pass

    @abstractmethod
    def import_prim(self, usd_prim):
        pass


