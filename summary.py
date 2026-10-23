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


def build_cleanup_summary(
    report_folder,
    semantic_folder
):

    inventory, name_lookup = (
        build_inventory(
            semantic_folder
        )
    )

    roots = (
        get_root_objects(
            report_folder,
            semantic_folder
        )
    )

    graph = (
        build_dependency_graph(
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

    unused_tables = sorted(
        all_tables
        - reachable_tables
    )

    reachable_measures = []
    unused_measures = []

    reachable_columns = []
    unused_columns = []

    for helper, item in inventory.items():

        if item["type"] == "measure":

            if helper in reachable:

                reachable_measures.append(
                    helper
                )

            else:

                unused_measures.append(
                    helper
                )

        elif item["type"] == "column":

            if helper in reachable:

                reachable_columns.append(
                    helper
                )

            else:

                unused_columns.append(
                    helper
                )

    summary = {

        "roots": sorted(
            roots
        ),

        "reachable": sorted(
            reachable
        ),

        "reachable_tables": sorted(
            reachable_tables
        ),

        "unused_tables": sorted(
            unused_tables
        ),

        "reachable_measures": sorted(
            reachable_measures
        ),

        "unused_measures": sorted(
            unused_measures
        ),

        "reachable_columns": sorted(
            reachable_columns
        ),

        "unused_columns": sorted(
            unused_columns
        )
    }

    return summary