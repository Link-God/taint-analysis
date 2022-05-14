from typing import TYPE_CHECKING

from .expr_visitor import ExprVisitor

if TYPE_CHECKING:
    from ..core.node_types import BlackBoxOrBuiltInNode, Node


class ControlFlowGraph:
    def __init__(self, nodes: list["Node"], blackbox_assignments: set["BlackBoxOrBuiltInNode"], filename: str):
        self.nodes: list["Node"] = nodes
        self.blackbox_assignments: set["BlackBoxOrBuiltInNode"] = blackbox_assignments
        self.filename: str = filename

    def __repr__(self):
        return "".join((f"Node: {i} {repr(n)}\n\n" for i, n in enumerate(self.nodes)))

    def __str__(self):
        return "".join((f"Node: {i} {str(n)}\n\n" for i, n in enumerate(self.nodes)))

    @classmethod
    def make_cfg(
        cls,
        tree,
        project_modules,
        local_modules,
        filename: str,
        module_definitions=None,
        allow_local_directory_imports=True,
    ):
        visitor = ExprVisitor(
            tree,
            project_modules,
            local_modules,
            filename,
            module_definitions,
            allow_local_directory_imports,
        )
        return cls(visitor.nodes, visitor.blackbox_assignments, filename)
