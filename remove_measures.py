from pathlib import Path
import re


def remove_measures(
    semantic_folder,
    measures_to_remove,
    apply_changes=False
):

    measures_to_remove = {
        measure.casefold()
        for measure in measures_to_remove
    }

    tables_folder = (
        Path(semantic_folder)
        / "definition"
        / "tables"
    )

    removed = []

    for table_file in tables_folder.rglob(
        "*.tmdl"
    ):

        try:

            lines = table_file.read_text(
                encoding="utf-8",
                errors="ignore"
            ).splitlines(
                keepends=True
            )

        except Exception:

            continue

        output = []

        i = 0

        while i < len(lines):

            line = lines[i]

            stripped = line.strip()

            #
            # Detect measure start
            #
            if stripped.startswith(
                "measure "
            ):

                measure_name = (
                    stripped
                    .replace(
                        "measure ",
                        "",
                        1
                    )
                    .split(
                        "=",
                        1
                    )[0]
                    .strip()
                    .strip("'")
                    .strip('"')
                    .casefold()
                )

                helper = (
                    f"{table_file.stem.casefold()}."
                    f"{measure_name}"
                )

                #
                # Remove the entire measure block
                #
                if helper in measures_to_remove:

                    removed.append(
                        helper
                    )

                    i += 1

                    while i < len(lines):

                        next_line = (
                            lines[i]
                            .strip()
                        )

                        if (
                            next_line.startswith(
                                "measure "
                            )
                            or next_line.startswith(
                                "column "
                            )
                            or next_line.startswith(
                                "partition "
                            )
                            or next_line.startswith(
                                "hierarchy "
                            )
                            or next_line.startswith(
                                "calculationGroup "
                            )
                        ):
                            break

                        i += 1

                    continue

            output.append(
                line
            )

            i += 1

        if apply_changes:

            table_file.write_text(
                "".join(output),
                encoding="utf-8"
            )

    return removed