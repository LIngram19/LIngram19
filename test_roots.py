from root_builder import (
    get_root_objects
)

roots = get_root_objects(
    r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.Report",
    r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.SemanticModel"
)

print()

print(
    f"Roots: "
    f"{len(roots)}"
)

print()

for root in sorted(
    roots
):
    print(root)