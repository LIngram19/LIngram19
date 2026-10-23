from cleanup_summary import (
    build_cleanup_summary
)

summary = (
    build_cleanup_summary(
        r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.Report",
        r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.SemanticModel"
    )
)

print()
print("=" * 60)
print("CLEANUP SUMMARY")
print("=" * 60)
print()

print(
    f"Roots: "
    f"{len(summary['roots'])}"
)

print(
    f"Reachable Objects: "
    f"{len(summary['reachable'])}"
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