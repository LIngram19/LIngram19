from dependency_graph import (
    build_dependency_graph
)

graph = build_dependency_graph(
    r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.SemanticModel"
)

print()

print(
    f"Graph Nodes: "
    f"{len(graph)}"
)

print(
    f"Dependency Links: "
    f"{sum(len(v) for v in graph.values())}"
)

print()

for name in sorted(graph)[:20]:

    print(
        name,
        "->",
        len(graph[name])
    )