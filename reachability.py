def get_reachable_nodes(
    graph,
    roots
):

    reachable = set()

    stack = list(
        roots
    )

    while stack:

        current = (
            stack.pop()
        )

        if current in reachable:
            continue

        reachable.add(
            current
        )

        stack.extend(
            graph.get(
                current,
                set()
            )
        )

    return reachable