from summary import (
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
    f"Reachable Tables: "
    f"{len(summary['reachable_tables'])}"
)

print(
    f"Unused Tables: "
    f"{len(summary['unused_tables'])}"
)

print()

print(
    f"Reachable Measures: "
    f"{len(summary['reachable_measures'])}"
)

print(
    f"Unused Measures: "
    f"{len(summary['unused_measures'])}"
)

print()

print(
    f"Reachable Columns: "
    f"{len(summary['reachable_columns'])}"
)

print(
    f"Unused Columns: "
    f"{len(summary['unused_columns'])}"
)

print()

print("UNUSED TABLES")
print("-" * 60)

for item in summary[
    "unused_tables"
]:

    print(item)

print()

print("UNUSED MEASURES")
print("-" * 60)

for item in summary[
    "unused_measures"
]:

    print(item)