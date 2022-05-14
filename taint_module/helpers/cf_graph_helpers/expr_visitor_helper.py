from collections import namedtuple

from taint_module.core.node_types import ConnectToExitNode

SavedVariable = namedtuple("SavedVariable", ("LHS", "RHS"))
BUILTINS = (
    "get",
    "Flask",
    "run",
    "replace",
    "read",
    "set_cookie",
    "make_response",
    "SQLAlchemy",
    "Column",
    "execute",
    "sessionmaker",
    "Session",
    "filter",
    "call",
    "render_template",
    "redirect",
    "url_for",
    "flash",
    "jsonify",
    # Django,
    "annotate",
    "extra",
    "order_by",
    "render",
    "aggregate",
    "objects",
    "all",
    "filter",
)
MUTATORS = (  # list.append(x) taints list if x is tainted
    "add",
    "append",
    "extend",
    "insert",
    "update",
)


def return_connection_handler(nodes, exit_node):
    """Connect all return statements to the Exit node."""
    for function_body_node in nodes:
        if isinstance(function_body_node, ConnectToExitNode):
            if exit_node not in function_body_node.outgoing:
                function_body_node.connect(exit_node)
