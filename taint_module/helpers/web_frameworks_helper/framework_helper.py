import ast

from more_itertools import last

from taint_module.helpers.core_helpers.ast_helper import get_call_names


def is_django_view_function(ast_node):
    if len(ast_node.args.args):
        first_arg_name = ast_node.args.args[0].arg
        return first_arg_name == "request"
    return False


def is_flask_route_function(ast_node):
    """Check whether function uses a route decorator."""
    for decorator in ast_node.decorator_list:
        if isinstance(decorator, ast.Call) and last(get_call_names(decorator.func)) == "route":
            return True
    return False


def is_function(function):
    """Always returns true because arg is always a function."""
    return True


def is_function_without_leading_(ast_node):
    if ast_node.name.startswith("_"):
        return False
    return True
