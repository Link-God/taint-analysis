"""
Global lookup table for constraints.

Uses control flow graph node as key and operates on bitvectors in the form of ints.
"""
import operator
from functools import reduce
from typing import TYPE_CHECKING, Iterable

from taint_module.control_flow_graph.graph import ControlFlowGraph
from taint_module.helpers.utils import Singleton

if TYPE_CHECKING:
    from taint_module.core.node_types import Node
__all__ = ["constraint_table"]


class ConstraintTableClass(metaclass=Singleton):
    def __init__(self):
        self._constraint_table: dict["Node", int] = {}

    @property
    def constraint_table(self):
        return self._constraint_table

    def initialize_constraint_table(self, graphs: Iterable[ControlFlowGraph]):
        """Collects all given cfg nodes and initializes the table with value 0."""

        self._constraint_table.update(dict.fromkeys((node for cfg in graphs for node in cfg.nodes), 0))

    def constraint_join(self, cfg_nodes: Iterable["Node"]):
        """Looks up all cfg_nodes and joins the bitvectors by using logical or."""

        return reduce(operator.or_, (self._constraint_table.get(cfg_node) for cfg_node in cfg_nodes), 0)

    def __getitem__(self, item):
        return self._constraint_table[item]

    def __setitem__(self, key, value):
        self._constraint_table[key] = value


constraint_table = ConstraintTableClass()
