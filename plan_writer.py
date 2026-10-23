from pathlib import Path

from cleanup_summary import (
    build_cleanup_summary
)


def write_cleanup_plan(
    report_folder,
    semantic_folder,
    output_file
):

    summary = (
        build_cleanup_summary(
            report_folder,
            semantic_folder
        )
    )

    lines = []

    lines.append(
        "=" * 60
    )

    lines.append(
        "CLEANUP PLAN"
    )

    lines.append(
        "=" * 60
    )

    lines.append("")

    #
    # Summary
    #

    lines.append(
        "SUMMARY"
    )

    lines.append(
        "-" * 60
    )

    lines.append(
        f"Roots: "
        f"{len(summary['roots'])}"
    )

    lines.append(
        f"Reachable Objects: "
        f"{len(summary['reachable'])}"
    )

    lines.append(
        f"Unused Tables: "
        f"{len(summary['unused_tables'])}"
    )

    lines.append(
        f"Unused Measures: "
        f"{len(summary['unused_measures'])}"
    )

    lines.append(
        f"Unused Columns: "
        f"{len(summary['unused_columns'])}"
    )

    lines.append(
        f"Relationships To Remove: "
        f"{len(summary['relationships_to_remove'])}"
    )

    lines.append(
        f"Expressions To Remove: "
        f"{len(summary['expressions_to_remove'])}"
    )

    lines.append("")

    #
    # Tables
    #

    lines.append(
        f"TABLES TO REMOVE "
        f"({len(summary['unused_tables'])})"
    )

    lines.append(
        "-" * 60
    )

    for item in summary[
        "unused_tables"
    ]:

        lines.append(
            item
        )

    lines.append("")

    #
    # Relationships
    #

    lines.append(
        f"RELATIONSHIPS TO REMOVE "
        f"({len(summary['relationships_to_remove'])})"
    )

    lines.append(
        "-" * 60
    )

    for item in summary[
        "relationships_to_remove"
    ]:

        lines.append(
            item
        )

    lines.append("")

    #
    # Expressions
    #

    lines.append(
        f"EXPRESSIONS TO REMOVE "
        f"({len(summary['expressions_to_remove'])})"
    )

    lines.append(
        "-" * 60
    )

    for item in summary[
        "expressions_to_remove"
    ]:

        lines.append(
            item
        )

    lines.append("")

    #
    # Measures
    #

    lines.append(
        f"MEASURES TO REMOVE "
        f"({len(summary['unused_measures'])})"
    )

    lines.append(
        "-" * 60
    )

    for item in summary[
        "unused_measures"
    ]:

        lines.append(
            item
        )

    lines.append("")

    #
    # Columns
    #

    lines.append(
        f"UNUSED COLUMNS "
        f"({len(summary['unused_columns'])})"
    )

    lines.append(
        "-" * 60
    )

    for item in summary[
        "unused_columns"
    ]:

        lines.append(
            item
        )

    Path(
        output_file
    ).write_text(
        "\n".join(lines),
        encoding="utf-8"
    )

    return summary