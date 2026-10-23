from model_parser import (
    build_inventory
)

from visual_parser import (
    get_visual_refs
)

from dependency_graph import (
    build_dependency_graph
)

from reachability import (
    get_reachable_nodes
)


semantic_folder = (
    r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.SemanticModel"
)

report_folder = (
    r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.Report"
)


inventory, name_lookup = (
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
    get_visual_refs(
        report_folder
    )
)

reachable = (
    get_reachable_nodes(
        graph,
        roots
    )
)

all_objects = {
    key
    for key, value
    in inventory.items()
    if value["type"]
    in (
        "measure",
        "column"
    )
}

unused = (
    all_objects
    - reachable
)

unused_measures = []
unused_columns = []

for item in sorted(
    unused
):

    obj_type = (
        inventory[item]["type"]
    )

    if obj_type == "measure":

        unused_measures.append(
            item
        )

    elif obj_type == "column":

        unused_columns.append(
            item
        )
print()

print(
    f"Unused Measures: "
    f"{len(unused_measures)}"
)

print()
print("Unused Measures")
print("-" * 60)

for measure in sorted(
    unused_measures
):
    print(measure)

print(
    f"Unused Columns: "
    f"{len(unused_columns)}"
)

print()

print(
    f"Total Objects: "
    f"{len(all_objects)}"
)

print(
    f"Reachable: "
    f"{len(reachable)}"
)

print(
    f"Unused: "
    f"{len(unused)}"
)

print()

for item in sorted(
    unused
)[:50]:

    print(item)