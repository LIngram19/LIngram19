from __future__ import annotations

from pathlib import Path
from typing import Dict, Set
import re

from report_usage_lib import (
    collect_report_usage,
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
        stripped_line.startswith("measure ")
        or stripped_line.startswith("column ")
        or stripped_line.startswith("partition ")
        or stripped_line.startswith("hierarchy ")
        or stripped_line.startswith("calculationGroup ")
    )


def parse_all_measure_blocks(
    model_tables_dir: Path,
) -> Dict[str, str]:

    measures: Dict[str, str] = {}

    for table_file in sorted(
        model_tables_dir.glob("*.tmdl")
    ):

        lines = table_file.read_text(
            encoding="utf-8",
            errors="ignore",
        ).splitlines()

        i = 0

        while i < len(lines):

            stripped = lines[i].strip()

            if not stripped.startswith(
                "measure "
            ):
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

            measures[
                measure_name
            ] = "\n".join(
                lines[
                    i:block_end
                ]
            )

            i = block_end

    return measures


def get_all_measure_names(
    model_tables_dir: Path,
) -> Set[str]:

    return set(
        parse_all_measure_blocks(
            model_tables_dir
        ).keys()
    )


def references_measure(
    expression: str,
    measure_name: str,
) -> bool:

    if not expression:
        return False

    escaped = re.escape(
        measure_name
    )

    return bool(
        re.search(
            rf"\[\s*{escaped}\s*\]",
            expression,
            flags=re.IGNORECASE,
        )
    )


def build_measure_dependency_graph(
    measure_sources: Dict[str, str],
) -> Dict[str, Set[str]]:

    graph: Dict[str, Set[str]] = {
        measure_name: set()
        for measure_name in measure_sources
    }

    for measure_name, expression in (
        measure_sources.items()
    ):

        for dependency_name in (
            measure_sources
        ):

            if (
                dependency_name
                == measure_name
            ):
                continue

            if references_measure(
                expression,
                dependency_name,
            ):

                graph[
                    measure_name
                ].add(
                    dependency_name
                )

    return graph

def get_model_referenced_measures(
    model_tables_dir: Path,
    measure_sources: Dict[str, str],
) -> Set[str]:

    referenced: Set[str] = set()

    for table_file in sorted(
        model_tables_dir.glob("*.tmdl")
    ):

        table_text = table_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        for (
            measure_name,
            measure_block,
        ) in measure_sources.items():

            #
            # Remove the measure's own definition so
            # self-references don't mark it as used.
            #
            remaining_text = table_text.replace(
                measure_block,
                "",
            )

            if references_measure(
                remaining_text,
                measure_name,
            ):
                referenced.add(
                    measure_name
                )

    return referenced

def get_used_measures(
    report_root: Path,
    model_tables_dir: Path,
) -> Set[str]:

    usage = collect_report_usage(
        report_root
    )

    report_measure_names: Set[str] = set()

    for measure_ref in (
        usage["measures"]
    ):

        if "::" not in measure_ref:
            continue

        _, measure_name = (
            measure_ref.split(
                "::",
                1,
            )
        )

        normalized = (
            normalize_name(
                measure_name
            )
        )

        if normalized:

            report_measure_names.add(
                normalized
            )

    measure_sources = (
        parse_all_measure_blocks(
            model_tables_dir
        )
    )

    dependency_graph = (
        build_measure_dependency_graph(
            measure_sources
        )
    )

    model_referenced = (
        get_model_referenced_measures(
            model_tables_dir,
            measure_sources,
        )
    )

    roots = (
        report_measure_names
        | model_referenced
    )

    active = set(roots)

    queue = list(roots)

    while queue:

        current = queue.pop()

        for dependency in (
            dependency_graph.get(
                current,
                set(),
            )
        ):

            if dependency not in active:

                active.add(
                    dependency
                )

                queue.append(
                    dependency
                )

    return active


def get_unused_measures(
    report_root: Path,
    model_tables_dir: Path,
) -> Set[str]:

    all_measures = get_all_measure_names(
        model_tables_dir
    )

    used_measures = get_used_measures(
        report_root,
        model_tables_dir,
    )

    return all_measures - used_measures


def main():

    model_tables_dir = (
        MODEL_ROOT
        / "definition"
        / "tables"
    )

    all_measures = (
        get_all_measure_names(
            model_tables_dir
        )
    )

    used_measures = (
        get_used_measures(
            REPORT_ROOT,
            model_tables_dir,
        )
    )

    unused_measures = (
        all_measures
        - used_measures
    )

    print()
    print("=" * 60)
    print("ALL MEASURES")
    print("=" * 60)
    print()

    for measure in sorted(
        all_measures
    ):
        print(measure)

    print()
    print(
        f"Total Measures: "
        f"{len(all_measures)}"
    )

    print()
    print("=" * 60)
    print("USED MEASURES")
    print("=" * 60)
    print()

    for measure in sorted(
        used_measures
    ):
        print(measure)

    print()
    print(
        f"Used Measures: "
        f"{len(used_measures)}"
    )

    print()
    print("=" * 60)
    print("UNUSED MEASURES")
    print("=" * 60)
    print()

    for measure in sorted(
        unused_measures
    ):
        print(measure)

    print()
    print(
        f"Unused Measures: "
        f"{len(unused_measures)}"
    )


if __name__ == "__main__":
    main()