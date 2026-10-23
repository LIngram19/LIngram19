import re

from model_parser import (
    build_inventory,
    normalize_name
)


def build_dependency_graph(
    semantic_folder
):

    inventory, name_lookup = (
        build_inventory(
            semantic_folder
        )
    )

    graph = {}

    #
    # Only measures can currently
    # have dependencies
    #
    measures = [
        item
        for item
        in inventory.values()
        if item["type"] == "measure"
    ]

    for measure in measures:

        helper_name = (
            measure["helper"]
        )

        graph[
            helper_name
        ] = set()

        dax = measure["dax"]

        if not dax:
            continue

        references = re.findall(
            r"\[([^\]]+)\]",
            dax
        )

        for ref in references:

            normalized = (
                normalize_name(
                    ref
                )
            )

            dependency = (
                name_lookup.get(
                    normalized
                )
            )

            if (
                dependency
                and dependency
                != helper_name
            ):

                graph[
                    helper_name
                ].add(
                    dependency
                )

    return graph