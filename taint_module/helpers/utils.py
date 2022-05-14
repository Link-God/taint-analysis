import os
from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    from taint_module.core.node_types import Node

from collections import defaultdict
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

from taint_module.core.node_types import AssignmentNode

if TYPE_CHECKING:

    from taint_module.analysis import Lattice
    from taint_module.core.node_types import Node


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def get_only_assignment(cfg_nodes: Iterable["Node"]) -> Iterator[AssignmentNode]:
    for node in filter(lambda n: isinstance(n, AssignmentNode), cfg_nodes):
        yield node


def build_definition_use_chain(cfg_nodes: Iterable["Node"], lattice: "Lattice"):
    definition_use = defaultdict(list)
    # For every node if it is definition
    for node in get_only_assignment(cfg_nodes):  # type: AssignmentNode
        for variable in node.right_hand_side_variables:
            # Loop through most of the nodes before it
            for earlier_node in lattice.get_elements_by_node(node):
                # and add them to the 'uses list' of each earlier node, when applicable
                # 'earlier node' here being a simplification
                if variable in earlier_node.left_hand_side:
                    definition_use[earlier_node].append(node)
    return definition_use


# todo mb prepare excluded_files
def discover_files(targets, excluded_files, recursive=False) -> list[str]:
    included_files: list[str] = list()
    excluded_list = excluded_files.split(",")
    for target in targets:
        if os.path.isdir(target):
            for root, _, files in os.walk(target):
                for file in files:
                    if file.endswith(".py") and file not in excluded_list:
                        fullpath = os.path.join(root, file)
                        included_files.append(fullpath)
                if not recursive:
                    break
        else:
            if target not in excluded_list:
                included_files.append(target)
    return included_files


def is_python_file(path) -> bool:
    p = Path(path)
    return p.is_file() and p.suffix == ".py"
