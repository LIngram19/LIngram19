import argparse
from pathlib import Path

from analyzers import (
    find_unused_columns,
    find_unused_expressions,
    find_unused_measures,
    find_unused_tables
)


# ============================================================
# OUTPUT HELPERS
# ============================================================

def print_header(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def print_section(title, total_count, items):

    print()

    if isinstance(items, dict):


        for status in [
            "UNUSED",
            "RELATIONSHIP_ONLY"
        ]:

            print()
            print("=" * 60)
            print(
                f"{status} "
                f"({len(items[status])})"
            )
            print("=" * 60)

            for name in sorted(items[status]):
                print(name)

        return

    print(
        f"{title}: "
        f"{len(items)}/{total_count}"
    )

    print("-" * 60)

    if not items:
        print("None")
        return

    for item in sorted(items):
        print(item)


def print_table_section(title, total_count, items):

    print()

    if isinstance(items, dict):

        print(
            f"{title}: "
            f"{total_count} total tables"
        )

        for status in [
            "UNUSED",
            "DAX_ONLY"
        ]:

            print()
            print("=" * 60)
            print(
                f"{status} "
                f"({len(items[status])})"
            )
            print("=" * 60)

            for name in sorted(items[status]):
                print(name)

        return

    print(
        f"{title}: "
        f"{len(items)}/{total_count}"
    )



# ============================================================
# REPORT LOCATOR
# ============================================================

def get_project_paths(project_root, report_name):
    """
    Locates the report and semantic model folders.
    """

    project_root = Path(project_root)

    report_folder = next(
        project_root.glob(f"{report_name}.Report"),
        None
    )

    semantic_folder = next(
        project_root.glob(f"{report_name}.SemanticModel"),
        None
    )

    if report_folder is None:
        raise FileNotFoundError(
            f"Could not find {report_name}.Report"
        )

    if semantic_folder is None:
        raise FileNotFoundError(
            f"Could not find {report_name}.SemanticModel"
        )

    return report_folder, semantic_folder


# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def analyze_expressions(report_folder, semantic_folder):
    return find_unused_expressions(
        report_folder,
        semantic_folder
    )


def analyze_measures(report_folder, semantic_folder):
    return find_unused_measures(
        report_folder,
        semantic_folder
    )


def analyze_columns(report_folder, semantic_folder):

    return find_unused_columns(
        report_folder,
        semantic_folder
    )


def analyze_tables(report_folder, semantic_folder):

    total_count, grouped, _ = (
        find_unused_tables(
            report_folder,
            semantic_folder
        )
    )

    return (
        total_count,
        grouped
    )


# ============================================================
# MAIN
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description="PBIP Cleanup Analyzer"
    )

    parser.add_argument(
        "--root",
        required=True,
        help="Root folder containing the PBIP project"
    )

    parser.add_argument(
        "--report",
        required=True,
        help="Report name (without .Report)"
    )

    parser.add_argument(
        "--check",
        choices=[
            "expressions",
            "measures",
            "columns",
            "tables",
            "all"
        ],
        default="all",
        help="Which object type to analyze"
    )

    args = parser.parse_args()

    report_folder, semantic_folder = get_project_paths(
        args.root,
        args.report
    )

    # ============================================================
    # DEBUG
    # ============================================================

    from pbip_parser import (
        get_tmdl_files,
        get_all_measures,
        get_all_tables,
    )

    files = get_tmdl_files(semantic_folder)

    print("\n" + "=" * 60)
    print("DEBUG")
    print("=" * 60)

    print(f"\nTMDL FILE COUNT: {len(files)}")

    for f in files[:10]:
        print(f)

    tables = get_all_tables(semantic_folder)

    print(f"\nTABLE COUNT: {len(tables)}")

    for table in sorted(list(tables))[:10]:
        print(table)

    measures = get_all_measures(semantic_folder)

    print(f"\nMEASURE COUNT: {len(measures)}")

    for measure in sorted(list(measures))[:20]:
        print(measure)

    print("\n" + "=" * 60)
    print("END DEBUG")
    print("=" * 60)

    print_header("PBIP ANALYSIS")

    print(f"Report: {args.report}")
    print(f"Report Folder: {report_folder}")
    print(f"Semantic Folder: {semantic_folder}")

    # --------------------------------------------------------
    # EXPRESSIONS
    # --------------------------------------------------------

    if args.check in ("expressions", "all"):

        total_count, unused_expressions = analyze_expressions(
            report_folder,
            semantic_folder
        )

        print_section(
            "Unused Expressions",
            total_count,
            unused_expressions
        )

    # --------------------------------------------------------
    # MEASURES
    # --------------------------------------------------------

    if args.check in ("measures", "all"):

        total_count, unused_measures = analyze_measures(
            report_folder,
            semantic_folder
        )

        print_section(
            "Unused Measures",
            total_count,
            unused_measures
        )

    # --------------------------------------------------------
    # COLUMNS
    # --------------------------------------------------------

    if args.check in ("columns", "all"):

        total_count, unused_columns = analyze_columns(
            report_folder,
            semantic_folder
        )

        print_section(
            "Possibly Unused Columns",
            total_count,
            unused_columns
        )

    # --------------------------------------------------------
    # TABLES
    # --------------------------------------------------------

    if args.check in ("tables", "all"):

        total_count, unused_tables = analyze_tables(
            report_folder,
            semantic_folder
        )

        print_table_section(
            "Unused Tables",
            total_count,
            unused_tables
        )


if __name__ == "__main__":
    main()