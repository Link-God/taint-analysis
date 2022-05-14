from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:

    from taint_module.control_flow_graph import ControlFlowGraph
    from taint_module.core.node_types import Node


class BaseAnalysis(ABC):
    cfg: "ControlFlowGraph"

    @abstractmethod
    def fix_point_method(self, cfg_node: "Node"):
        pass

    @classmethod
    @abstractmethod
    def analyse(cls, cfg_list: list["ControlFlowGraph"]):
        pass
