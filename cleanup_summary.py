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

from expression_parser import (
    get_expressions_to_remove
)


def build_cleanup_summary(
    report_folder,
    semantic_folder
):

    #
    # Inventory
    #
    inventory, name_lookup = (
        build_inventory(
            semantic_folder
        )
    )

    #
    # Dependency Graph
    #
    graph = (
        build_dependency_graph(
            semantic_folder
        )
    )

    #
    # Roots
    #
    roots = (
        get_root_objects(
            report_folder,
            semantic_folder
        )
    )

    #
    # Reachability
    #
    reachable = (
        get_reachable_nodes(
            graph,
            roots
        )
    )

    #
    # Reachable Tables
    #
    reachable_tables = (
        get_reachable_tables(
            reachable,
            inventory
        )
    )

    #
    # All Tables
    #
    all_tables = {
        item["table"]
        for item
        in inventory.values()
    }

    unused_tables = sorted(
        all_tables
        - reachable_tables
    )

    #
    # Measures
    #
    reachable_measures = []
    unused_measures = []

    #
    # Columns
    #
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

    #
    # Relationships
    #
    relationships_to_remove = (
        get_relationships_to_remove(
            semantic_folder,
            unused_tables
        )
    )

    #
    # Expressions
    #
    expressions_to_remove = (
        get_expressions_to_remove(
            semantic_folder,
            reachable_tables
        )
    )

    return {

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
        ),

        "relationships_to_remove": sorted(
            relationships_to_remove
        ),

        "expressions_to_remove": sorted(
            expressions_to_remove
        )
    }