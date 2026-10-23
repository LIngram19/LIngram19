from visual_parser import (
    get_visual_refs
)

from model_parser import (
    build_inventory
)


refs = get_visual_refs(
    r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.Report"
)

print()

print(
    f"QueryRefs: "
    f"{len(refs)}"
)

print()

for ref in sorted(refs)[:50]:

    print(ref)


inventory, name_lookup = (
    build_inventory(
        r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.SemanticModel"
    )
)

inventory_keys = set(
    inventory.keys()
)

matches = {
    ref
    for ref in refs
    if ref in inventory_keys
}

print()

print(
    f"Matched Roots: "
    f"{len(matches)}"
)

print()

for item in sorted(matches):

    print(item)