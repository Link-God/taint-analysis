from typing import TYPE_CHECKING

from .base_analysis import BaseAnalysis

if TYPE_CHECKING:

    from taint_module.control_flow_graph.graph import ControlFlowGraph
    from taint_module.core.node_types import Node

from typing import Iterable, Iterator

from ..core.node_types import AssignmentNode
from ..helpers.utils import get_only_assignment
from .constraint_table import constraint_table


class Lattice:
    def __init__(self, cfg_nodes: Iterable["Node"]):
        self.el2bv: dict[AssignmentNode:int] = dict()  # Element to bitvector dictionary
        self.bv2el: list[AssignmentNode] = []  # Bitvector to element list
        for i, e in enumerate(get_only_assignment(cfg_nodes)):
            # Give each element a unique shift of 1
            self.el2bv[e] = 0b1 << i
            self.bv2el.insert(0, e)

    def get_elements_by_node(self, source_node: "Node") -> Iterator[AssignmentNode]:
        for element in self.get_elements(constraint_table[source_node]):
            if element is not source_node:
                yield element

    def get_elements(self, number) -> list[AssignmentNode]:
        if number == 0:
            return []

        elements: list[AssignmentNode] = []
        # Turn number into a binary string of length len(self.bv2el)
        binary_string = format(number, "0" + str(len(self.bv2el)) + "b")
        for i, bit in enumerate(binary_string):
            if bit == "1":
                elements.append(self.bv2el[i])
        return elements

    def in_constraint(self, node1, node2) -> bool:
        """
        Checks if node1 is in node2's constraints
        For instance, if node1 = 010 and node2 = 110:
        010 & 110 = 010 -> has the element.
        """
        constraint = constraint_table[node2]
        if constraint == 0b0:
            return False

        try:
            value = self.el2bv[node1]
        except KeyError:
            return False

        return constraint & value != 0


class ReachingDefinitionsTaintAnalysis(BaseAnalysis):
    def __init__(self, cfg):
        self.cfg: "ControlFlowGraph" = cfg
        self.lattice: Lattice = Lattice(cfg.nodes)

    def fix_point_method(self, cfg_node):
        """The most important part of PyT, where we perform
        the variant of reaching definitions to find where sources reach.
        """
        join = self.join(cfg_node)
        # Assignment check
        if isinstance(cfg_node, AssignmentNode):
            arrow_result = join

            # Reassignment check
            if cfg_node.left_hand_side not in cfg_node.right_hand_side_variables:
                # Get previous assignments of cfg_node.left_hand_side and remove them from JOIN
                arrow_result = self.arrow(join, cfg_node.left_hand_side)

            arrow_result = arrow_result | self.lattice.el2bv[cfg_node]
            constraint_table[cfg_node] = arrow_result
        # Default case
        else:
            constraint_table[cfg_node] = join

    def fixpoint_runner(self):
        """Work list algorithm that runs the fixpoint algorithm."""
        cgf_nodes = self.cfg.nodes

        while cgf_nodes:
            x_i = constraint_table[cgf_nodes[0]]  # x_i = q[0].old_constraint
            self.fix_point_method(cgf_nodes[0])  # y = F_i(x_1, ..., x_n);
            y = constraint_table[cgf_nodes[0]]  # y = cgf_nodes[0].new_constraint

            if y != x_i:
                for node in self.dep(cgf_nodes[0]):  # for (v in dep(v_i))
                    cgf_nodes.append(node)  # cgf_nodes.append(v):
                constraint_table[
                    cgf_nodes[0]
                ] = y  # cgf_nodes[0].old_constraint = cgf_nodes[0].new_constraint # x_i = y
            cgf_nodes = cgf_nodes[1:]  # cgf_nodes = cgf_nodes.tail()  # The list minus the head

    @classmethod
    def analyse(cls, cfg_list: Iterable["ControlFlowGraph"]):
        """Analyse a list of control flow graphs with a given analysis type."""
        for cfg in cfg_list:
            cls(cfg).fixpoint_runner()

    @staticmethod
    def join(cfg_node):
        """Joins all constraints of the ingoing nodes and returns them.
        This represents the JOIN auxiliary definition from Schwartzbach."""
        return constraint_table.constraint_join(cfg_node.ingoing)

    def arrow(self, join, _id):
        """Removes all previous assignments from JOIN that have the same left hand side.
        This represents the arrow id definition from Schwartzbach."""
        r = join
        for node in self.lattice.get_elements(join):
            if node.left_hand_side == _id:
                r = r ^ self.lattice.el2bv[node]
        return r

    @staticmethod
    def dep(q_1):
        """Represents the dep mapping from Schwartzbach."""
        yield from q_1.outgoing
