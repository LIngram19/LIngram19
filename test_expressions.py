from model_parser import (
    build_inventory
)

from root_builder import (
    get_root_objects
)

from dependency_graph import (
    build_dependency_graph
)

from reachability import (
    get_reachable_nodes
)

from reachable_tables import (
    get_reachable_tables
)

from expression_parser import (
    get_expressions_to_remove
)


semantic_folder = (
    r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.SemanticModel"
)

report_folder = (
    r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.Report"
)

inventory, _ = (
    build_inventory(
        semantic_folder
    )
)

graph = (
    build_dependency_graph(
        semantic_folder
    )
)

roots = (
    get_root_objects(
        report_folder,
        semantic_folder
    )
)

reachable = (
    get_reachable_nodes(
        graph,
        roots
    )
)

reachable_tables = (
    get_reachable_tables(
        reachable,
        inventory
    )
)

expressions = (
    get_expressions_to_remove(
        semantic_folder,
        reachable_tables
    )
)

print()

print(
    f"Expressions To Remove: "
    f"{len(expressions)}"
)

print()

for expression in expressions:

    print(
        expression
    )