from __future__ import annotations

from pathlib import Path
from datetime import datetime


def write_cleanup_report(
    output_root: Path,
    report_name: str,
    removed_tables,
    removed_relationships,
    removed_expressions,
    removed_measures,
    removed_refs,
    removed_query_groups,
) -> Path:

    summary_root = (
        output_root
        / "Cleanup Summaries"
    )

    summary_root.mkdir(
        exist_ok=True
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    report_path = (
        summary_root
        / (
            f"{report_name}"
            f"_cleanup_report_"
            f"{timestamp}.txt"
        )
    )

    with report_path.open(
        "w",
        encoding="utf-8",
    ) as f:

        f.write(
            "POWER BI CLEANUP REPORT\n"
        )

        f.write(
            "=" * 80 + "\n\n"
        )

        f.write(
            f"Report Name: "
            f"{report_name}\n"
        )

        f.write(
            f"Generated: "
            f"{datetime.now()}\n\n"
        )

        f.write(
            "SUMMARY\n"
        )

        f.write(
            "-" * 40 + "\n"
        )

        f.write(
            f"Tables Removed: "
            f"{len(removed_tables)}\n"
        )

        f.write(
            f"Relationships Removed: "
            f"{len(removed_relationships)}\n"
        )

        f.write(
            f"Expressions Removed: "
            f"{len(removed_expressions)}\n"
        )

        f.write(
            f"Measures Removed: "
            f"{len(removed_measures)}\n"
        )

        f.write(
            f"Model References Removed: "
            f"{len(removed_refs)}\n"
        )

        f.write(
            f"Query Groups Removed: "
            f"{len(removed_query_groups)}\n\n"
        )

        sections = [
            (
                "REMOVED TABLES",
                removed_tables,
            ),
            (
                "REMOVED RELATIONSHIPS",
                removed_relationships,
            ),
            (
                "REMOVED EXPRESSIONS",
                removed_expressions,
            ),
            (
                "REMOVED MEASURES",
                removed_measures,
            ),
            (
                "REMOVED MODEL REFERENCES",
                removed_refs,
            ),
            (
                "REMOVED QUERY GROUPS",
                removed_query_groups,
            ),
        ]

        for title, items in sections:

            f.write(
                title + "\n"
            )

            f.write(
                "-" * 40 + "\n"
            )

            if items:

                for item in sorted(
                    str(x)
                    for x in items
                ):
                    f.write(
                        f"{item}\n"
                    )

            else:

                f.write(
                    "None\n"
                )

            f.write("\n")

    return report_path