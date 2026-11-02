from __future__ import annotations

from pathlib import Path
from typing import Set

from unused_measure_detector import (
    get_unused_measures,
)


from config import MODEL_ROOT

from config import REPORT_ROOT


def normalize_name(
    value: str | None,
) -> str | None:

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = value.replace(
        "'",
        "",
    ).replace(
        '"',
        "",
    )

    if (
        value.startswith("[")
        and value.endswith("]")
    ):
        value = value[1:-1]

    return value.strip() or None


def is_sibling_object(
    stripped_line: str,
) -> bool:

    return (
        stripped_line.startswith(
            "measure "
        )
        or stripped_line.startswith(
            "column "
        )
        or stripped_line.startswith(
            "partition "
        )
        or stripped_line.startswith(
            "hierarchy "
        )
        or stripped_line.startswith(
            "calculationGroup "
        )
    )


def remove_unused_measures(
    model_tables_dir: Path,
    unused_measures: Set[str],
) -> Set[str]:

    unused_measures = {
        normalize_name(
            measure
        )
        for measure in unused_measures
        if normalize_name(
            measure
        )
    }

    removed: Set[str] = set()

    for table_file in sorted(
        model_tables_dir.glob(
            "*.tmdl"
        )
    ):

        lines = table_file.read_text(
            encoding="utf-8",
            errors="ignore",
        ).splitlines()

        output: list[str] = []

        i = 0

        while i < len(lines):

            stripped = (
                lines[i].strip()
            )

            if not stripped.startswith(
                "measure "
            ):

                output.append(
                    lines[i]
                )

                i += 1
                continue

            name_part = stripped[
                len("measure "):
            ]

            if "=" in name_part:

                measure_name = (
                    name_part
                    .split(
                        "=",
                        1,
                    )[0]
                    .strip()
                )

            else:

                measure_name = (
                    name_part.strip()
                )

            measure_name = (
                normalize_name(
                    measure_name
                )
                or measure_name
            )

            measure_indent = (
                len(lines[i])
                - len(
                    lines[i].lstrip()
                )
            )

            block_end = i + 1

            while (
                block_end
                < len(lines)
            ):

                current_line = (
                    lines[block_end]
                )

                stripped_line = (
                    current_line.strip()
                )

                if not stripped_line:

                    block_end += 1
                    continue

                current_indent = (
                    len(current_line)
                    - len(
                        current_line.lstrip()
                    )
                )

                if (
                    current_indent
                    == measure_indent
                    and is_sibling_object(
                        stripped_line
                    )
                ):
                    break

                block_end += 1

            if (
                measure_name
                in unused_measures
            ):

                removed.add(
                    measure_name
                )

                # print(
                #     f"Removing measure: "
                #     f"{measure_name}"
                # )

                i = block_end
                continue

            output.extend(
                lines[
                    i:block_end
                ]
            )

            i = block_end

        table_file.write_text(
            "\n".join(
                output
            )
            + "\n",
            encoding="utf-8",
        )

    return removed


def main():

    model_tables_dir = (
        MODEL_ROOT
        / "definition"
        / "tables"
    )

    unused_measures = (
        get_unused_measures(
            REPORT_ROOT,
            model_tables_dir,
        )
    )

    print()
    print("=" * 60)
    print("UNUSED MEASURES FOUND")
    print("=" * 60)
    print()

    # for measure in sorted(
    #     unused_measures
    # ):
    #     print(measure)

    print()
    print(
        f"Unused Measures: "
        f"{len(unused_measures)}"
    )

    removed = (
        remove_unused_measures(
            model_tables_dir,
            unused_measures,
        )
    )

    print()
    print("=" * 60)
    print("REMOVED MEASURES")
    print("=" * 60)
    print()

    # for measure in sorted(
    #     removed
    # ):
    #     print(measure)

    print()
    print(
        f"Removed: "
        f"{len(removed)}"
    )

    print()


if __name__ == "__main__":
    main()