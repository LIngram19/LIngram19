from pathlib import Path
import re

from model_parser import (
    normalize_name,
    build_inventory
)


def get_rls_refs(
    semantic_folder
):

    inventory, name_lookup = (
        build_inventory(
            semantic_folder
        )
    )

    refs = set()

    roles_folder = (
        Path(semantic_folder)
        / "definition"
        / "roles"
    )

    if not roles_folder.exists():

        return refs

    for role_file in roles_folder.rglob(
        "*.tmdl"
    ):

        try:

            text = role_file.read_text(
                encoding="utf-8",
                errors="ignore"
            )

        except Exception:

            continue

        #
        # Capture references like:
        #
        # 'Customer'[UPN]
        # Customer[UPN]
        #
        matches = re.findall(
            r"'?([^'\[]+)'?\[([^\]]+)\]",
            text
        )

        for table_name, object_name in matches:

            helper_name = (
                f"{normalize_name(table_name)}."
                f"{normalize_name(object_name)}"
            )

            if helper_name in inventory:

                refs.add(
                    helper_name
                )

        #
        # Also capture measure references:
        #
        # [Measure Name]
        #
        measure_matches = re.findall(
            r"\[([^\]]+)\]",
            text
        )

        for measure_name in measure_matches:

            helper_name = (
                name_lookup.get(
                    normalize_name(
                        measure_name
                    )
                )
            )

            if helper_name:

                refs.add(
                    helper_name
                )

    return refs