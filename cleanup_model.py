import argparse
from pathlib import Path
from datetime import datetime

from analyzers import (
    find_unused_expressions,
    find_unused_measures,
    find_unused_tables
)

from cleanup_helpers import (
    create_backup,
    write_plan,
    remove_table_files,
    remove_relationships,
    remove_expressions,
    remove_measures
)

MAX_PASSES = 5


# ============================================================
# PATHS
# ============================================================

def get_project_paths(
    project_root,
    report_name
):

    project_root = Path(
        project_root
    )

    report_folder = next(
        project_root.glob(
            f"{report_name}.Report"
        ),
        None
    )

    semantic_folder = next(
        project_root.glob(
            f"{report_name}.SemanticModel"
        ),
        None
    )

    if report_folder is None:

        raise FileNotFoundError(
            f"Could not find "
            f"{report_name}.Report"
        )

    if semantic_folder is None:

        raise FileNotFoundError(
            f"Could not find "
            f"{report_name}.SemanticModel"
        )

    return (
        report_folder,
        semantic_folder
    )


# ============================================================
# HELPERS
# ============================================================

def print_header(title):

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def get_unused_tables(
    report_folder,
    semantic_folder
):

    _, grouped, _ = (
        find_unused_tables(
            report_folder,
            semantic_folder
        )
    )

    return grouped.get(
        "UNUSED",
        []
    )


def get_unused_expressions(
    report_folder,
    semantic_folder
):

    _, expressions = (
        find_unused_expressions(
            report_folder,
            semantic_folder
        )
    )

    return expressions


def get_unused_measures(
    report_folder,
    semantic_folder
):

    _, measures = (
        find_unused_measures(
            report_folder,
            semantic_folder
        )
    )

    if isinstance(
        measures,
        dict
    ):

        return measures.get(
            "UNUSED",
            []
        )

    return measures


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "PBIP Cleanup Utility"
        )
    )

    parser.add_argument(
        "--root",
        required=True,
        help=(
            "Folder containing PBIP"
        )
    )

    parser.add_argument(
        "--report",
        required=True,
        help=(
            "Report name "
            "(without extension)"
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Actually modify files"
        )
    )

    args = parser.parse_args()

    run_timestamp = (
        datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    (
        report_folder,
        semantic_folder
    ) = get_project_paths(
        args.root,
        args.report
    )

    print_header(
        "PBIP CLEANUP"
    )

    print(
        f"Report: {args.report}"
    )

    print(
        f"Apply Changes: "
        f"{args.apply}"
    )

    if args.apply:

        backup_folder = (
            create_backup(
                semantic_folder,
                args.report
            )
        )

    else:

        backup_folder = (
            "No backup created "
            "(dry run)"
        )

    safe_report_name = (
        args.report
        .replace("/", "_")
        .replace("\\", "_")
    )

    plan_file = (
        Path(args.root)
        / (
            f"{safe_report_name}"
            f"_cleanup_plan_{run_timestamp}.txt"
        )
    )

    pass_number = 1

    all_removed_tables = set()
    all_removed_relationships = set()
    all_removed_expressions = set()
    all_removed_measures = set()

    table_analysis_complete = False

    while pass_number <= MAX_PASSES:

        print_header(
            f"CLEANUP PASS {pass_number}"
        )

        if table_analysis_complete:

            unused_tables = []

        else:

            unused_tables = (
                get_unused_tables(
                    report_folder,
                    semantic_folder
                )
            )

            if len(unused_tables) == 0:

                table_analysis_complete = True

                print(
                    "Table cleanup stabilized."
                )

        unused_expressions = (
            get_unused_expressions(
                report_folder,
                semantic_folder
            )
        )

        unused_measures = (
            get_unused_measures(
                report_folder,
                semantic_folder
            )
        )

        change_count = (
            len(unused_tables)
            + len(unused_expressions)
            + len(unused_measures)
        )

        print(
            f"Tables: {len(unused_tables)}"
        )

        print(
            f"Expressions: "
            f"{len(unused_expressions)}"
        )

        print(
            f"Measures: "
            f"{len(unused_measures)}"
        )

        if change_count == 0:

            print(
                "\nNo additional "
                "cleanup candidates found."
            )

            break

        removed_tables = (
            remove_table_files(
                semantic_folder,
                unused_tables,
                args.apply
            )
        )

        removed_relationships = (
            remove_relationships(
                semantic_folder,
                removed_tables,
                args.apply
            )
        )

        removed_expressions = (
            remove_expressions(
                semantic_folder,
                unused_expressions,
                args.apply
            )
        )

        removed_measures = (
            remove_measures(
            semantic_folder,
            unused_measures,
            args.apply
    )
)

        all_removed_tables.update(
            removed_tables
        )

        all_removed_relationships.update(
            removed_relationships
        )

        all_removed_expressions.update(
            removed_expressions
        )

        all_removed_measures.update(
            removed_measures
        )

        print(
            f"Removed Tables: "
            f"{len(removed_tables)}"
        )

        print(
            f"Removed Relationships: "
            f"{len(removed_relationships)}"
        )

        print(
            f"Removed Expressions: "
            f"{len(removed_expressions)}"
        )

        print(
            f"Removed Measures: "
            f"{len(removed_measures)}"
        )

        print()
        print()
        print(
            f"Running Total Tables: "
            f"{len(all_removed_tables)}"
        )

        print(
            f"Running Total Relationships: "
            f"{len(all_removed_relationships)}"
        )

        print(
            f"Running Total Expressions: "
            f"{len(all_removed_expressions)}"
        )

        print(
            f"Running Total Measures: "
            f"{len(all_removed_measures)}"
        )

        if not args.apply:
            break

        pass_number += 1

    write_plan(
    plan_file,
    args.report,
    max(1, pass_number - 1),
    sorted(all_removed_tables),
    sorted(all_removed_relationships),
    sorted(all_removed_expressions),
    sorted(all_removed_measures)
)
    # ============================================================
    # SUMMARY
    # ============================================================

    print_header(
        "CLEANUP SUMMARY"
    )

    print(
        f"Tables: "
        f"{len(all_removed_tables)}"
    )

    print(
        f"Relationships: "
        f"{len(all_removed_relationships)}"
    )

    print(
        f"Expressions: "
        f"{len(all_removed_expressions)}"
    )

    print(
        f"Measures: "
        f"{len(all_removed_measures)}"
    )

    print()

    print(
        "Cleanup Plan:"
    )

    print(
        plan_file
    )

    print()

    print(
        "Backup:"
    )

    print(
        backup_folder
    )

    if not args.apply:

        print()

        print(
            "DRY RUN ONLY"
        )

        print(
            "Run again with "
            "--apply "
            "to modify files."
        )


if __name__ == "__main__":

    main()
