from datetime import datetime
from pathlib import Path

from project_paths import (
    get_project_paths
)

from cleanup_helpers import (
    create_backup
)

from cleanup_summary import (
    build_cleanup_summary
)

from plan_writer import (
    write_cleanup_plan
)

from remove_relationships import (
    remove_relationships
)

from variation_cleanup import (
    cleanup_variations
)

from remove_expressions import (
    remove_expressions
)

from remove_tables import (
    remove_tables
)

from model_cleanup import (
    cleanup_model
)

from remove_measures import (
    remove_measures
)

from role_cleanup import (
    cleanup_roles
)

def execute_cleanup(
    report_folder,
    semantic_folder,
    apply_changes=False
):

    print()
    print("=" * 60)
    print("BUILDING CLEANUP SUMMARY")
    print("=" * 60)

    summary = (
        build_cleanup_summary(
            report_folder,
            semantic_folder
        )
    )

    print()

    print(
        f"Unused Tables: "
        f"{len(summary['unused_tables'])}"
    )

    print(
        f"Unused Measures: "
        f"{len(summary['unused_measures'])}"
    )

    print(
        f"Unused Columns: "
        f"{len(summary['unused_columns'])}"
    )

    print(
        f"Relationships To Remove: "
        f"{len(summary['relationships_to_remove'])}"
    )

    print(
        f"Expressions To Remove: "
        f"{len(summary['expressions_to_remove'])}"
    )

    print()
    print("=" * 60)
    print("WRITING CLEANUP PLAN")
    print("=" * 60)

    report_name = (
        Path(
            semantic_folder
        ).stem
    )

    timestamp = (
        datetime.now()
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    cleanup_plan_file = (
        Path(
            semantic_folder
        ).parent
        / (
            f"{report_name}"
            f"_cleanup_plan_"
            f"{timestamp}.txt"
        )
    )

    write_cleanup_plan(
        report_folder,
        semantic_folder,
        cleanup_plan_file
    )

    print(
        f"Cleanup Plan: "
        f"{cleanup_plan_file}"
    )

    if not apply_changes:

        print()
        print("=" * 60)
        print("DRY RUN ONLY")
        print("=" * 60)

        return summary

    print()
    print("=" * 60)
    print("CREATING BACKUP")
    print("=" * 60)

    backup_folder = create_backup(
        semantic_folder,
        report_name
    )

    print(
        f"Backup Created: "
        f"{backup_folder}"
    )

    print()
    print("=" * 60)
    print("REMOVING RELATIONSHIPS")
    print("=" * 60)

    removed_relationships = (
        remove_relationships(
            semantic_folder,
            summary[
                "relationships_to_remove"
            ],
            apply_changes=True
        )
    )

    print(
        f"Removed Relationships: "
        f"{len(removed_relationships)}"
    )

    print()
    print("=" * 60)
    print("CLEANING VARIATIONS")
    print("=" * 60)

    removed_variations = (
        cleanup_variations(
            semantic_folder,
            apply_changes=True
        )
    )

    print(
        f"Removed Variations: "
        f"{len(removed_variations)}"
    )

    print()
    print("=" * 60)
    print("REMOVING EXPRESSIONS")
    print("=" * 60)

    removed_expressions = (
        remove_expressions(
            semantic_folder,
            summary[
                "expressions_to_remove"
            ],
            apply_changes=True
        )
    )

    print(
        f"Removed Expressions: "
        f"{len(removed_expressions)}"
    )

    print()
    print("=" * 60)
    print("REMOVING TABLES")
    print("=" * 60)

    removed_tables = (
        remove_tables(
            semantic_folder,
            summary[
                "unused_tables"
            ],
            apply_changes=True
        )
    )

    print(
        f"Removed Tables: "
        f"{len(removed_tables)}"
    )

    print()
    print("=" * 60)
    print("CLEANING MODEL")
    print("=" * 60)

    model_results = (
        cleanup_model(
            semantic_folder,
            apply_changes=True
        )
    )

    print(
        f"Removed Table References: "
        f"{len(model_results['removed_refs'])}"
    )

    print(
        f"Remaining Tables: "
        f"{len(model_results['remaining_tables'])}"
    )
    print()
    print("=" * 60)
    print("CLEANING ROLES")
    print("=" * 60)

    role_results = (
        cleanup_roles(
            semantic_folder,
            apply_changes=True
        )
    )

    print(
        f"Removed Role Permissions: "
        f"{len(role_results['removed_permissions'])}"
    )

    print(
        f"Updated Roles: "
        f"{len(role_results['roles_updated'])}"
    )
    print()
    print("=" * 60)
    print("REMOVING MEASURES")
    print("=" * 60)

    removed_measures = (
        remove_measures(
            semantic_folder,
            summary[
                "unused_measures"
            ],
            apply_changes=True
        )
    )

    explicitly_removed_measures = (
        len(removed_measures)
    )

    implicitly_removed_measures = max(
        0,
        len(
            summary[
                "unused_measures"
            ]
        )
        - explicitly_removed_measures
    )

    print(
        f"Measures Removed Via Table Deletion: "
        f"{implicitly_removed_measures}"
    )

    print(
        f"Measures Removed From Remaining Tables: "
        f"{explicitly_removed_measures}"
    )

    print(
        f"Total Measures Removed: "
        f"{len(summary['unused_measures'])}"
    )

    print()
    print("=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)

    return summary


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "Power BI PBIP Cleanup Tool"
        )
    )

    parser.add_argument(
        "pbip_root",
        help=(
            "Folder containing "
            "<Report>.Report and "
            "<Report>.SemanticModel"
        )
    )

    parser.add_argument(
        "report_name",
        help=(
            "PBIP report name"
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Apply changes. "
            "Without this flag "
            "the tool runs as a dry run."
        )
    )

    args = parser.parse_args()

    paths = (
        get_project_paths(
            args.pbip_root,
            args.report_name
        )
    )

    execute_cleanup(
        report_folder=(
            paths["report_folder"]
        ),
        semantic_folder=(
            paths["semantic_folder"]
        ),
        apply_changes=args.apply
    )