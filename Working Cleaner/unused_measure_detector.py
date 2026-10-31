from __future__ import annotations

from pathlib import Path
from typing import Dict, Set
import re

from report_usage_lib import (
    collect_report_usage,
)


MODEL_ROOT = Path(
    r"c:\Users\LINGRAM\Documents\PBI Test Files\5 Year Look Back.SemanticModel"
)

REPORT_ROOT = Path(
    r"c:\Users\LINGRAM\Documents\PBI Test Files\5 Year Look Back.Report"
)


def normalize_name(value: str | None) -> str | None:
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    value = value.replace("'", "").replace('"', "")

    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]

    return value.strip() or None


def parse_table_name_from_tmdl(table_file: Path) -> str | None:

    lines = table_file.read_text(
        encoding="utf-8",
        errors="ignore"
    ).splitlines()

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("table "):
            return normalize_name(
                stripped[len("table "):].strip()
            )

    return table_file.stem


def parse_all_measure_blocks(
    model_tables_dir: Path,
) -> Dict[str, str]:

    measures: Dict[str, str] = {}

    for table_file in sorted(model_tables_dir.glob("*.tmdl")):

        lines = table_file.read_text(
            encoding="utf-8",
            errors="ignore"
        ).splitlines()

        i = 0

        while i < len(lines):

            stripped = lines[i].strip()

            if stripped.startswith("measure "):

                name_part = stripped[len("measure "):]

                if " = " in name_part:
                    measure_name = name_part.split(
                        " = ",
                        1
                    )[0].strip()

                elif "=" in name_part:
                    measure_name = name_part.split(
                        "=",
                        1
                    )[0].strip()

                else:
                    measure_name = name_part.strip()

                measure_name = (
                    normalize_name(measure_name)
                    or measure_name
                )

                j = i + 1

                while j < len(lines):

                    next_line = lines[j]

                    if (
                        next_line.strip()
                        and not next_line.startswith(
                            (" ", "\t")
                        )
                    ):
                        break

                    j += 1

                measures[measure_name] = "\n".join(
                    lines[i:j]
                )

                i = j
                continue

            i += 1

    return measures


def references_measure(
    expression: str,
    measure_name: str,
) -> bool:

    pattern = re.escape(measure_name)

    if re.search(
        rf"\[\s*{pattern}\s*\]",
        expression,
        flags=re.IGNORECASE,
    ):
        return True

    if re.search(
        rf"(?<![A-Za-z0-9_]){pattern}(?![A-Za-z0-9_])",
        expression,
        flags=re.IGNORECASE,
    ):
        return True

    return False


def build_measure_dependency_graph(
    measure_sources: Dict[str, str]
) -> Dict[str, Set[str]]:

    graph = {
        measure_name: set()
        for measure_name in measure_sources
    }

    for measure_name, expression in measure_sources.items():

        for dependency_name in measure_sources:

            if dependency_name == measure_name:
                continue

            if references_measure(
                expression,
                dependency_name,
            ):
                graph[measure_name].add(
                    dependency_name
                )

    return graph


def compute_active_measure_set(
    report_root: Path,
    model_tables_dir: Path,
) -> Set[str]:

    usage = collect_report_usage(report_root)

    report_measures: Set[str] = set()

    for measure_ref in usage["measures"]:

        if "::" not in measure_ref:
            continue

        _, measure_name = measure_ref.split(
            "::",
            1
        )

        if measure_name:
            report_measures.add(measure_name)

    measure_sources = parse_all_measure_blocks(
        model_tables_dir
    )

    graph = build_measure_dependency_graph(
        measure_sources
    )

    active = set(report_measures)

    queue = list(report_measures)

    while queue:

        current = queue.pop()

        for dependency in graph.get(
            current,
            set()
        ):

            if dependency not in active:
                active.add(dependency)
                queue.append(dependency)

    return active


def find_unused_measures(
    report_root: Path,
    model_tables_dir: Path,
):

    all_measures = parse_all_measure_blocks(
        model_tables_dir
    )

    active_measures = compute_active_measure_set(
        report_root,
        model_tables_dir,
    )

    unused_measures = (
        set(all_measures.keys())
        - active_measures
    )

    return (
        all_measures,
        active_measures,
        unused_measures,
    )


def main():

    model_tables_dir = (
        MODEL_ROOT
        / "definition"
        / "tables"
    )

    (
        all_measures,
        active_measures,
        unused_measures,
    ) = find_unused_measures(
        REPORT_ROOT,
        model_tables_dir,
    )

    print()
    print(
        "=============================="
    )
    print("MEASURE USAGE REPORT")
    print(
        "=============================="
    )
    print()

    print(
        f"Total Measures : {len(all_measures)}"
    )

    print(
        f"Used Measures  : {len(active_measures)}"
    )

    print(
        f"Unused Measures: {len(unused_measures)}"
    )

    print()

    print(
        "===== UNUSED MEASURES ====="
    )

    for measure in sorted(unused_measures):
        print(measure)


if __name__ == "__main__":
    main()