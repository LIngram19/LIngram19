from __future__ import annotations

from pathlib import Path
from typing import Dict, Set
import re

from report_usage_lib import (
    collect_report_usage,
    parse_measure_blocks,
    parse_table_name_from_file,
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


def parse_all_measure_blocks(model_tables_dir: Path) -> Dict[str, str]:
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
                    measure_name = name_part.split(" = ", 1)[0].strip()
                elif "=" in name_part:
                    measure_name = name_part.split("=", 1)[0].strip()
                else:
                    measure_name = name_part.strip()

                measure_name = normalize_name(measure_name)

                j = i + 1

                while j < len(lines):
                    next_line = lines[j]

                    if next_line.strip() and not next_line.startswith((" ", "\t")):
                        break

                    j += 1

                block_text = "\n".join(lines[i:j])

                if measure_name:
                    measures[measure_name] = block_text

                i = j
                continue

            i += 1

    return measures


def references_measure(expression: str, measure_name: str) -> bool:
    pattern = re.escape(measure_name)

    return bool(
        re.search(
            rf"\[\s*{pattern}\s*\]",
            expression,
            flags=re.IGNORECASE,
        )
    )


def build_measure_dependency_graph(
    measure_sources: Dict[str, str]
) -> Dict[str, Set[str]]:
    graph: Dict[str, Set[str]] = {
        name: set()
        for name in measure_sources
    }

    for measure_name, expression in measure_sources.items():
        for dep_name in measure_sources:
            if dep_name == measure_name:
                continue

            if references_measure(expression, dep_name):
                graph[measure_name].add(dep_name)

    return graph


def compute_active_measure_set(
    report_root: Path,
    model_tables_dir: Path,
) -> Set[str]:

    usage = collect_report_usage(report_root)

    report_measure_names: Set[str] = set()

    for measure_ref in usage["measures"]:
        if "::" not in measure_ref:
            continue

        _, measure_name = measure_ref.split("::", 1)

        if measure_name:
            report_measure_names.add(measure_name)

    measure_sources = parse_all_measure_blocks(model_tables_dir)

    dependency_graph = build_measure_dependency_graph(
        measure_sources
    )

    active = set(report_measure_names)

    queue = list(report_measure_names)

    while queue:
        current = queue.pop()

        for dep in dependency_graph.get(current, set()):
            if dep not in active:
                active.add(dep)
                queue.append(dep)

    return active


def compute_keep_tables(
    report_root: Path,
    model_tables_dir: Path,
) -> Set[str]:

    usage = collect_report_usage(report_root)

    keep_tables: Set[str] = set()

    for table_name in usage["tables"]:
        normalized = normalize_name(table_name)

        if normalized:
            keep_tables.add(normalized)

    for column_ref in usage["columns"]:
        if "::" in column_ref:
            table_name = column_ref.split("::", 1)[0]
            keep_tables.add(normalize_name(table_name))

    for measure_ref in usage["measures"]:
        if "::" in measure_ref:
            table_name = measure_ref.split("::", 1)[0]
            keep_tables.add(normalize_name(table_name))

    return {
        t
        for t in keep_tables
        if t
    }


def main():

    REPORT_ROOT = Path(
        r"c:\Users\LINGRAM\Documents\PBI Test Files\5 Year Look Back.Report"
    )

    MODEL_ROOT = Path(
        r"c:\Users\LINGRAM\Documents\PBI Test Files\5 Year Look Back.SemanticModel"
    )

    model_tables_dir = MODEL_ROOT / "definition" / "tables"

    active_measures = compute_active_measure_set(
        REPORT_ROOT,
        model_tables_dir,
    )

    keep_tables = compute_keep_tables(
        REPORT_ROOT,
        model_tables_dir,
    )

    print("\n=== ACTIVE MEASURES ===")

    for measure in sorted(active_measures):
        print(measure)

    print(
        f"\nActive Measures: {len(active_measures)}"
    )

    print("\n=== KEEP TABLES ===")

    for table in sorted(keep_tables):
        print(table)

    print(
        f"\nKeep Tables: {len(keep_tables)}"
    )


if __name__ == "__main__":
    main()