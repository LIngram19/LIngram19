from dependency_graph import (
    build_dependency_graph
)

from visual_parser import (
    get_visual_refs
)

from reachability import (
    get_reachable_nodes
)

graph = build_dependency_graph(
    r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.SemanticModel"
)

roots = get_visual_refs(
    r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.Report"
)

reachable = (
    get_reachable_nodes(
        graph,
        roots
    )
)

print()

print(
    f"Roots: "
    f"{len(roots)}"
)

print(
    f"Reachable: "
    f"{len(reachable)}"
)

print()

for item in sorted(
    reachable
):

    print(item)