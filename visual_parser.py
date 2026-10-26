from pathlib import Path
import re

from model_parser import (
    normalize_name
)


def get_visual_refs(
    report_folder
):

    refs = set()

    report_folder = Path(
        report_folder
    )

    files = list(
        report_folder.rglob(
            "*.json"
        )
    )

    print(
        f"JSON Files Found: "
        f"{len(files)}"
    )

    for file in files:

        try:

            text = file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception:

            continue

        #
        # queryRef
        #
        for match in re.findall(
            r'"queryRef"\s*:\s*"([^"]+)"',
            text,
            flags=re.IGNORECASE
        ):

            normalized = normalize_name(
                match
            )

            #
            # Only keep fully-qualified
            # references like:
            #
            #   table.measure
            #   table.column
            #
            if "." in normalized:

                refs.add(
                    normalized
                )

        #
        # Entity
        #
        for match in re.findall(
            r'"Entity"\s*:\s*"([^"]+)"',
            text,
            flags=re.IGNORECASE
        ):

            refs.add(
                normalize_name(
                    match
                )
            )

        #
        # Property
        #
        for match in re.findall(
            r'"Property"\s*:\s*"([^"]+)"',
            text,
            flags=re.IGNORECASE
        ):

            refs.add(
                normalize_name(
                    match
                )
            )

        #
        # Entity + Property
        #
        entity_property_matches = re.findall(
            r'"Entity"\s*:\s*"([^"]+)"[\s\S]{0,500}?"Property"\s*:\s*"([^"]+)"',
            text,
            flags=re.IGNORECASE
        )

        for entity, prop in entity_property_matches:

            refs.add(
                normalize_name(
                    entity
                )
            )

            refs.add(
                normalize_name(
                    prop
                )
            )

            refs.add(
                normalize_name(
                    f"{entity}.{prop}"
                )
            )

        #
        # Field Parameter References
        #
        field_parameter_matches = re.findall(
            r"'''([^']+)''\[([^\]]+)\]",
            text,
            flags=re.IGNORECASE
        )

        for table_name, object_name in field_parameter_matches:

            refs.add(
                normalize_name(
                    table_name
                )
            )

            refs.add(
                normalize_name(
                    object_name
                )
            )

            refs.add(
                normalize_name(
                    f"{table_name}.{object_name}"
                )
            )

    print(
        f"References Found: "
        f"{len(refs)}"
    )
    print()
    print("=" * 60)
    print("VISUAL REFS SAMPLE")
    print("=" * 60)

    for ref in sorted(refs):

        if (
            "net fees" in ref
            or "backlog" in ref
        ):

            print(ref)
    return refs