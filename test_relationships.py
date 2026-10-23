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

from relationship_parser import (
    get_relationships_to_remove
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

all_tables = {
    item["table"]
    for item in inventory.values()
}

unused_tables = (
    all_tables
    - reachable_tables
)

relationships = (
    get_relationships_to_remove(
        semantic_folder,
        unused_tables
    )
)

print()

print(
    f"Unused Tables: "
    f"{len(unused_tables)}"
)

print(
    f"Relationships To Remove: "
    f"{len(relationships)}"
)

print()

for relationship in relationships:

    print(
        relationship
    )