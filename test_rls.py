from rls_parser import (
    get_rls_refs
)

refs = get_rls_refs(
    r"C:\Users\LINGRAM\Documents\PBI Test Files\FFMU.SemanticModel"
)

print()

print(
    f"RLS Refs: "
    f"{len(refs)}"
)

print()

for ref in sorted(refs):

    print(ref)