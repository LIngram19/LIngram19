from __future__ import annotations

from pathlib import Path
from typing import Dict, Set, Iterable
import re

from report_usage_lib import (
    collect_report_usage,
    parse_table_name_from_file,
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

def is_generated_date_table(
    table_name: str | None,
) -> bool:

    normalized = normalize_name(
        table_name
    )

    if not normalized:
        return False

    return (
        normalized.startswith(
            "LocalDateTable_"
        )
        or normalized.startswith(
            "DateTableTemplate_"
        )
    )

def get_all_model_tables(
    model_tables_dir: Path,
) -> Set[str]:

    tables: Set[str] = set()

    for table_file in sorted(
        model_tables_dir.glob("*.tmdl")
    ):

        table_name = parse_table_name_from_file(
            table_file
        )

        if not table_name:
            continue

        #
        # Ignore Power BI generated
        # LocalDateTable_* and
        # DateTableTemplate_* tables
        #
        if is_generated_date_table(
            table_name
        ):
            continue

        normalized = normalize_name(
            table_name
        )

        if normalized:
            tables.add(normalized)

    return tables




def parse_all_measure_blocks(
    model_tables_dir: Path,
) -> Dict[str, str]:

    measures: Dict[str, str] = {}

    for table_file in sorted(model_tables_dir.glob("*.tmdl")):

        lines = table_file.read_text(
            encoding="utf-8",
            errors="ignore",
        ).splitlines()

        i = 0

        while i < len(lines):

            stripped = lines[i].strip()

            if stripped.startswith("measure "):

                name_part = stripped[len("measure "):]

                if " = " in name_part:
                    measure_name = name_part.split(
                        " = ",
                        1,
                    )[0].strip()

                elif "=" in name_part:
                    measure_name = name_part.split(
                        "=",
                        1,
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

    if not expression:
        return False

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
    measure_sources: Dict[str, str],
) -> Dict[str, Set[str]]:

    graph: Dict[str, Set[str]] = {
        name: set()
        for name in measure_sources
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


def find_used_measure_names(
    report_root: Path,
    model_tables_dir: Path,
) -> Set[str]:

    usage = collect_report_usage(report_root)

    report_measure_names: Set[str] = set()

    for measure_ref in usage["measures"]:

        if "::" not in measure_ref:
            continue

        _, measure_name = measure_ref.split(
            "::",
            1,
        )

        if measure_name:
            report_measure_names.add(
                measure_name
            )

    measure_sources = parse_all_measure_blocks(
        model_tables_dir
    )

    graph = build_measure_dependency_graph(
        measure_sources
    )

    active = set(report_measure_names)

    queue = list(report_measure_names)

    while queue:

        current = queue.pop()

        for dependency in graph.get(
            current,
            set(),
        ):

            if dependency not in active:
                active.add(dependency)
                queue.append(dependency)

    return active


def find_measure_owner_table(
    model_tables_dir: Path,
    measure_name: str,
) -> str | None:

    normalized_measure = (
        normalize_name(measure_name)
        or measure_name
    )

    for table_file in sorted(
        model_tables_dir.glob("*.tmdl")
    ):

        table_name = parse_table_name_from_file(
            table_file
        )

        if not table_name:
            continue

        for line in table_file.read_text(
            encoding="utf-8",
            errors="ignore",
        ).splitlines():

            stripped = line.strip()

            if not stripped.startswith("measure "):
                continue

            name_part = stripped[len("measure "):]

            if " = " in name_part:
                candidate = name_part.split(
                    " = ",
                    1,
                )[0].strip()

            elif "=" in name_part:
                candidate = name_part.split(
                    "=",
                    1,
                )[0].strip()

            else:
                candidate = name_part.strip()

            if (
                normalize_name(candidate)
                == normalized_measure
            ):
                return table_name

    return None

def collect_role_permission_tables(
    model_roles_dir: Path,
) -> Set[str]:

    protected: Set[str] = set()

    if not model_roles_dir.exists():
        return protected

    role_files = list(
        sorted(model_roles_dir.glob("*.tmdl"))
    )

    legacy_roles_file = (
        model_roles_dir.parent
        / "roles.tmdl"
    )

    if legacy_roles_file.exists():
        role_files.append(
            legacy_roles_file
        )

    for role_file in role_files:

        text = role_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        #
        # Protect tables that have
        # tablePermission definitions.
        #
        for match in re.finditer(
            r"tablePermission\s+(['\"]?)(.+?)\1\s*=",
            text,
        ):

            table_name = normalize_name(
                match.group(2)
            )

            if table_name:
                protected.add(table_name)

        #
        # Protect tables referenced
        # inside DAX expressions.
        #
        quoted_table_refs = re.findall(
            r"'([^']+)'\s*\[",
            text,
            flags=re.IGNORECASE,
        )

        for table_name in quoted_table_refs:

            normalized = normalize_name(
                table_name
            )

            if normalized:
                protected.add(normalized)

        #
        # Protect tables referenced as:
        # TableName[Column]
        #
        unquoted_table_refs = re.findall(
            r"(?<!')\b([A-Za-z0-9_]+)\s*\[",
            text,
            flags=re.IGNORECASE,
        )

        for table_name in unquoted_table_refs:

            normalized = normalize_name(
                table_name
            )

            if normalized:
                protected.add(normalized)

    return protected


def extract_table_names_from_expression(
    expression: str,
    model_table_names: Iterable[str],
) -> Set[str]:

    if not expression:
        return set()

    refs: Set[str] = set()

    normalized_tables = []

    for name in model_table_names:
        normalized = normalize_name(name)

        if normalized:
            normalized_tables.append(normalized)

    for table_name in sorted(
        normalized_tables,
        key=len,
        reverse=True,
    ):

        escaped = re.escape(table_name)

        #
        # Match actual DAX table references:
        #   'Table'[Column]
        #   Table[Column]
        #
        patterns = [
            rf"'{escaped}'\s*\[",
            rf"{escaped}\s*\[",
        ]

        for pattern in patterns:

            if re.search(
                pattern,
                expression,
                flags=re.IGNORECASE,
            ):
                refs.add(table_name)
                break

    return refs

def collect_tables_referenced_anywhere_in_dax(
    model_tables_dir: Path,
) -> Set[str]:

    referenced_tables: Set[str] = set()

    model_table_names = {
        normalize_name(
            parse_table_name_from_file(path)
        )
        for path in sorted(
            model_tables_dir.glob("*.tmdl")
        )
        if parse_table_name_from_file(path)
    }

    model_table_names.discard(None)

    #
    # Scan every measure in the model.
    #
    measure_sources = parse_all_measure_blocks(
        model_tables_dir
    )

    for expression in measure_sources.values():

        referenced_tables |= (
            extract_table_names_from_expression(
                expression,
                model_table_names,
            )
        )

    #
    # Scan every table file for DAX column
    # expressions as well.
    #
    for table_file in sorted(
        model_tables_dir.glob("*.tmdl")
    ):

        text = table_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        referenced_tables |= (
            extract_table_names_from_expression(
                text,
                model_table_names,
            )
        )

    return referenced_tables

def extract_source_block_references(
    source_text: str,
    model_table_names: Iterable[str],
) -> Set[str]:

    refs: Set[str] = set()

    if not source_text:
        return refs

    for table_name in sorted(
        model_table_names,
        key=len,
        reverse=True,
    ):

        normalized = normalize_name(
            table_name
        )

        if not normalized:
            continue

        escaped = re.escape(normalized)

        patterns = [
            rf'#"{escaped}"',
            rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])",
        ]

        for pattern in patterns:
            if re.search(
                pattern,
                source_text,
                flags=re.IGNORECASE,
            ):
                refs.add(normalized)
                break

    return refs


def collect_tables_referenced_in_m_queries(
    model_tables_dir: Path,
) -> Set[str]:

    referenced_tables: Set[str] = set()

    model_table_names = {
        normalize_name(
            parse_table_name_from_file(path)
        )
        for path in sorted(
            model_tables_dir.glob("*.tmdl")
        )
        if parse_table_name_from_file(path)
    }

    model_table_names.discard(None)

    for table_file in sorted(
        model_tables_dir.glob("*.tmdl")
    ):

        current_table = normalize_name(
            parse_table_name_from_file(
                table_file
            )
        )

        text = table_file.read_text(
            encoding="utf-8",
            errors="ignore",
        )

        #
        # Find every partition source block.
        #
        source_blocks = re.findall(
            r"source\s*=\s*(.*?)(?=\n\s*annotation\b|\n\s*partition\b|\Z)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )

        for source_block in source_blocks:

            refs = extract_source_block_references(
                source_block,
                model_table_names,
            )

            if current_table:
                refs.discard(current_table)

            referenced_tables |= refs

    return referenced_tables

def collect_tables_used_by_active_measures(
    model_tables_dir: Path,
    used_measure_names: Set[str],
) -> Set[str]:

    all_measure_sources = parse_all_measure_blocks(
        model_tables_dir
    )

    if not all_measure_sources:
        return set()

    graph = build_measure_dependency_graph(
        all_measure_sources
    )

    model_table_names = {
        normalize_name(
            parse_table_name_from_file(path)
        )
        for path in sorted(
            model_tables_dir.glob("*.tmdl")
        )
        if parse_table_name_from_file(path)
    }

    model_table_names.discard(None)

    queue = list(used_measure_names)

    seen: Set[str] = set()

    used_tables: Set[str] = set()

    while queue:

        current = queue.pop()

        if current in seen:
            continue

        seen.add(current)

        owner_table = find_measure_owner_table(
            model_tables_dir,
            current,
        )

        if owner_table:

            normalized = normalize_name(
                owner_table
            )

            if normalized:
                used_tables.add(normalized)

        expression = all_measure_sources.get(
            current,
            "",
        )

        used_tables |= (
            extract_table_names_from_expression(
                expression,
                model_table_names,
            )
        )

        for dependency in graph.get(
            current,
            set(),
        ):

            if dependency not in seen:
                queue.append(dependency)

    return used_tables


def compute_keep_tables(
    report_root: Path,
    model_tables_dir: Path,
    model_roles_dir: Path,
) -> Set[str]:
    usage = collect_report_usage(report_root)

    keep: Set[str] = set()

    for table_name in usage["tables"]:

        normalized = normalize_name(
            table_name
        )

        if normalized:
            keep.add(normalized)

    for column_ref in usage["columns"]:

        if "::" not in column_ref:
            continue

        table_name = column_ref.split(
            "::",
            1,
        )[0]

        normalized = normalize_name(
            table_name
        )

        if normalized:
            keep.add(normalized)

    for measure_ref in usage["measures"]:

        if "::" not in measure_ref:
            continue

        table_name = measure_ref.split(
            "::",
            1,
        )[0]

        normalized = normalize_name(
            table_name
        )

        if normalized:
            keep.add(normalized)

    used_measure_names = find_used_measure_names(
        report_root,
        model_tables_dir,
    )

    keep |= collect_tables_used_by_active_measures(
    model_tables_dir,
    used_measure_names,
)

    #
    # Protect tables referenced anywhere
    # in model DAX.
    #
    keep |= collect_tables_referenced_anywhere_in_dax(
        model_tables_dir,
    )

    keep |= collect_role_permission_tables(
        model_roles_dir,
    )
    #
# Protect tables referenced from
# M query source blocks.
#
    keep |= collect_tables_referenced_in_m_queries(
        model_tables_dir,
    )
    return keep



def get_unused_tables() -> Set[str]:

    model_tables_dir = (
        MODEL_ROOT
        / "definition"
        / "tables"
    )

    model_roles_dir = (
        MODEL_ROOT
        / "definition"
        / "roles"
    )

    keep_tables = compute_keep_tables(
        REPORT_ROOT,
        model_tables_dir,
        model_roles_dir,
    )

    all_tables = get_all_model_tables(
        model_tables_dir
    )

    return all_tables - keep_tables


def main():

    unused_tables = get_unused_tables()

    model_tables_dir = (
        MODEL_ROOT
        / "definition"
        / "tables"
    )

    model_roles_dir = (
        MODEL_ROOT
        / "definition"
        / "roles"
    )

    all_tables = get_all_model_tables(
        model_tables_dir
    )

    keep_tables = compute_keep_tables(
        REPORT_ROOT,
        model_tables_dir,
        model_roles_dir,
    )

    print()
    print("=" * 60)
    print("TABLE USAGE REPORT")
    print("=" * 60)
    print()

    print(f"Total Tables : {len(all_tables)}")
    print(f"Used Tables  : {len(keep_tables)}")
    print(f"Unused Tables: {len(unused_tables)}")

    print()
    print("=" * 60)
    print("UNUSED TABLES")
    print("=" * 60)
    print()

    for table_name in sorted(unused_tables):
        print(table_name)
if __name__ == "__main__":
    main()