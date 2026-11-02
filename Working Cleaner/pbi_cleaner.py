from __future__ import annotations

import time

from backup_creator import (
    backup_semantic_model,
)

from unused_table_detector import (
    get_unused_tables,
)

from unused_table_remover import (
    remove_unused_tables,
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

from unused_measure_detector import (
    get_unused_measures,
)

from unused_measure_remover import (
    remove_unused_measures,
)

from config import (
    MODEL_ROOT,
    REPORT_ROOT,
    REPORT_NAME,
)

from cleanup_report import (
    write_cleanup_report,
)

TOTAL_STEPS = 6


def print_step(
    step_number: int,
    title: str,
):
    print()
    print("=" * 80)
    print(
        f"[{step_number}/{TOTAL_STEPS}] {title}"
    )
    print("=" * 80)


def main():

    run_start = time.time()

    print()
    print("=" * 80)
    print("POWER BI CLEANUP")
    print("=" * 80)

    print()

    print(
        f"Report Name : {REPORT_NAME}"
    )

    print(
        f"Model Path  : {MODEL_ROOT}"
    )

    print(
        f"Report Path : {REPORT_ROOT}"
    )

    print()

    if not MODEL_ROOT.exists():

        raise FileNotFoundError(
            f"Semantic model not found:\n"
            f"{MODEL_ROOT}"
        )

    if not REPORT_ROOT.exists():

        raise FileNotFoundError(
            f"Report not found:\n"
            f"{REPORT_ROOT}"
        )

    #
    # STEP 1
    #
    print_step(
        1,
        "CREATE BACKUP",
    )

    step_start = time.time()

    backup_path = backup_semantic_model(
        MODEL_ROOT
    )

    print()

    print(
        f"Backup Created: "
        f"{backup_path}"
    )

    print(
        f"Completed in "
        f"{time.time() - step_start:.2f}s"
    )

    #
    # Single source of truth
    #
    print()
    print("Scanning model...")

    unused_tables = get_unused_tables()

    print(
        f"Unused Tables Detected: "
        f"{len(unused_tables)}"
    )

    model_tables_dir = (
        MODEL_ROOT
        / "definition"
        / "tables"
    )

    #
    # STEP 2
    #
    print_step(
        2,
        "REMOVE UNUSED TABLES",
    )

    step_start = time.time()

    removed_tables = remove_unused_tables(
        model_tables_dir,
        unused_tables,
    )

    print()

    print(
        f"Tables Removed: "
        f"{len(removed_tables)}"
    )

    print(
        f"Completed in "
        f"{time.time() - step_start:.2f}s"
    )

    #
    # STEP 3
    #
    print_step(
        3,
        "REMOVE RELATIONSHIPS",
    )

    step_start = time.time()

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

    print(
        f"Completed in "
        f"{time.time() - step_start:.2f}s"
    )

    #
    # STEP 4
    #
    print_step(
        4,
        "REMOVE EXPRESSIONS",
    )

    step_start = time.time()

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

    print(
        f"Completed in "
        f"{time.time() - step_start:.2f}s"
    )

    #
    # STEP 5
    #
    print_step(
        5,
        "CLEAN MODEL",
    )

    step_start = time.time()

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

    print(
        f"Completed in "
        f"{time.time() - step_start:.2f}s"
    )

    #
    # STEP 6
    #
    print_step(
        6,
        "REMOVE UNUSED MEASURES",
    )

    step_start = time.time()

    unused_measures = (
        get_unused_measures(
            REPORT_ROOT,
            model_tables_dir,
        )
    )

    print()

    print(
        f"Unused Measures Detected: "
        f"{len(unused_measures)}"
    )

    removed_measures = (
        remove_unused_measures(
            model_tables_dir,
            unused_measures,
        )
    )

    print()

    print(
        f"Measures Removed: "
        f"{len(removed_measures)}"
    )

    print(
        f"Completed in "
        f"{time.time() - step_start:.2f}s"
    )

    #
    # SUMMARY
    #
    print()
    print("=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)

    print()

    print(
        f"Backup Created          : "
        f"{backup_path.name}"
    )

    print(
        f"Unused Tables Identified : "
        f"{len(unused_tables)}"
    )

    print(
        f"Tables Removed           : "
        f"{len(removed_tables)}"
    )

    print(
        f"Relationships Removed    : "
        f"{len(removed_relationships)}"
    )

    print(
        f"Expressions Removed      : "
        f"{len(removed_expressions)}"
    )

    print(
        f"Measures Removed         : "
        f"{len(removed_measures)}"
    )

    print(
        f"Model References Removed : "
        f"{len(model_results['removed_refs'])}"
    )

    print(
        f"Query Groups Removed     : "
        f"{len(model_results['removed_query_groups'])}"
    )

    report_file = write_cleanup_report(
        MODEL_ROOT.parent,
        REPORT_NAME,
        removed_tables,
        removed_relationships,
        removed_expressions,
        removed_measures,
        model_results["removed_refs"],
        model_results["removed_query_groups"],
    )

    print(
        f"Total Runtime            : "
        f"{time.time() - run_start:.2f}s"
    )

    print()

    print(
        f"Cleanup Report Saved     : "
        f"{report_file}"
    )

    print()

if __name__ == "__main__":
    main()