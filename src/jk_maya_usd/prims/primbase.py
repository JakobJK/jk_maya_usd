from abc import ABC, abstractmethod

class PrimBase(ABC):
    @abstractmethod
    def export_node(self, stage: str, dag_node:str, target: str):
        """This will export a node from Maya to the USD stage.

        Args:
            stage (_type_): The current stage we are exporting to.
            dag_node (_type_): The full path of the dag_node from Maya.
            target (_type_): The full path in the usd stage where the prim will be created.

        Returns:
            prim: The newly added prim.
        """
        pass

    @abstractmethod
    def import_prim(self, stage, usd_prim):
        pass