from __future__ import annotations

from unused_table_detector import (
    get_unused_tables,
)

from unused_table_remover import (
    remove_unused_tables,
    MODEL_ROOT,
)

from relationship_remover import (
    remove_relationships,
)

from relationship_detector import (
    get_relationships_to_remove,
)

from expression_detector import (
    get_unused_expressions,
)

from expression_remover import (
    remove_expressions,
)

from model_cleaner import (
    clean_model,
)

def main():

    print()
    print("=" * 80)
    print("POWER BI CLEANUP")
    print("=" * 80)
    print()

    #
    # Single source of truth
    #
    unused_tables = get_unused_tables()

    print(
        f"Unused Tables Detected: "
        f"{len(unused_tables)}"
    )

    #
    # Step 1
    # Remove table TMDL files
    #
    print()
    print("=" * 80)
    print("STEP 1 - REMOVE UNUSED TABLES")
    print("=" * 80)

    model_tables_dir = (
        MODEL_ROOT
        / "definition"
        / "tables"
    )

    removed_tables = remove_unused_tables(
        model_tables_dir,
        unused_tables,
    )

    print()
    print(
        f"Tables Removed: "
        f"{len(removed_tables)}"
    )

    #
    # Step 2
    # Remove relationships referencing
    # those same unused tables
    #
    print()
    print("=" * 80)
    print("STEP 2 - REMOVE RELATIONSHIPS")
    print("=" * 80)

    relationships_to_remove = (
        get_relationships_to_remove(
            unused_tables
        )
    )

    removed_relationships = (
        remove_relationships(
            relationships_to_remove
        )
    )

    print()
    print(
        f"Relationships Removed: "
        f"{len(removed_relationships)}"
    )

    print()
    print("=" * 80)
    print("STEP 3 - REMOVE EXPRESSIONS")
    print("=" * 80)

    unused_expressions = (
        get_unused_expressions()
    )

    removed_expressions = (
        remove_expressions(
            unused_expressions
        )
    )

    print()
    print(
        f"Expressions Removed: "
        f"{len(removed_expressions)}"
    )

    print()
    print("=" * 80)
    print("STEP 4 - CLEAN MODEL")
    print("=" * 80)

    model_results = clean_model(
        removed_tables
    )

    print()

    print(
        f"Ref Tables Removed: "
        f"{len(model_results['removed_refs'])}"
    )

    print(
        f"Query Groups Removed: "
        f"{len(model_results['removed_query_groups'])}"
    )
    #
    # Summary
    #
    print()
    print("=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)

    print()

    print(
        f"Unused Tables Identified : "
        f"{len(unused_tables)}"
    )

    print(
        f"Tables Removed          : "
        f"{len(removed_tables)}"
    )

    print(
        f"Relationships Removed   : "
        f"{len(removed_relationships)}"
    )

    print(
        f"Expressions Removed     : "
        f"{len(removed_expressions)}"
    )
    print()


if __name__ == "__main__":
    main()