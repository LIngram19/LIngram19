from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple


def normalize_name(value: str | None) -> str | None:
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None

    # Strip all single and double quotes before comparison so values like
    # `'Table'.'Column'` and `Table.Column` resolve to the same normalized name.
    value = value.replace("'", "").replace('"', "")
    value = value.strip()
    if not value:
        return None

    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"[", "'", '"'}:
        value = value[1:-1]
    return value.strip() or None


def collect_report_usage(report_root: Path) -> Dict[str, Set[str]]:
    """Return a usage summary of tables, columns, and measures referenced in the report JSON files."""
    tables: Set[str] = set()
    columns: Set[str] = set()
    measures: Set[str] = set()

    def visit(node):
        if isinstance(node, dict):
            if "SourceRef" in node:
                entity = node["SourceRef"].get("Entity")
                if entity:
                    tables.add(normalize_name(entity) or entity)

            if "Measure" in node:
                measure_def = node["Measure"]
                if isinstance(measure_def, dict):
                    expr = measure_def.get("Expression") or {}
                    entity = expr.get("SourceRef", {}).get("Entity")
                    property_name = measure_def.get("Property")
                    if entity and property_name:
                        n_entity = normalize_name(entity) or entity
                        n_property = normalize_name(property_name) or property_name
                        measures.add(f"{n_entity}::{n_property}")

            if "Column" in node:
                column_def = node["Column"]
                if isinstance(column_def, dict):
                    expr = column_def.get("Expression") or {}
                    entity = expr.get("SourceRef", {}).get("Entity")
                    property_name = column_def.get("Property")
                    if entity and property_name:
                        n_entity = normalize_name(entity) or entity
                        n_property = normalize_name(property_name) or property_name
                        columns.add(f"{n_entity}::{n_property}")

            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for item in node:
                visit(item)

    for json_path in sorted(report_root.rglob("*.json")):
        try:
            text = json_path.read_text(encoding="utf-8")
            payload = json.loads(text)
        except Exception:
            continue
        visit(payload)

    return {
        "tables": tables,
        "columns": columns,
        "measures": measures,
    }


def parse_table_name_from_file(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"(?m)^\s*table\s+(.+?)\s*$", text)
    if not match:
        return None
    return normalize_name(match.group(1))


def parse_measure_blocks(path: Path) -> List[Tuple[str, int, int]]:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    blocks: List[Tuple[str, int, int]] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("measure "):
            name_text = stripped[len("measure ") :]
            if " = " in name_text:
                measure_name = name_text.split(" = ", 1)[0].strip()
            elif "=" in name_text:
                measure_name = name_text.split("=", 1)[0].strip()
            else:
                measure_name = name_text.strip()
            name = normalize_name(measure_name)
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if not next_line.strip():
                    j += 1
                    continue
                if not next_line.startswith((" ", "\t")):
                    break
                j += 1
            blocks.append((name or "", i, j))
            i = j
            continue
        i += 1
    return blocks


def read_model_table_names(model_tables_dir: Path) -> Dict[str, Path]:
    names: Dict[str, Path] = {}
    for file_path in sorted(model_tables_dir.glob("*.tmdl")):
        table_name = parse_table_name_from_file(file_path)
        if table_name:
            names[table_name] = file_path
    return names


def parse_relationship_blocks(file_path: Path) -> List[Tuple[int, int, List[str]]]:
    """Return list of (start_idx, end_idx, relationship_tables) blocks."""
    lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    blocks: List[Tuple[int, int, List[str]]] = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("relationship "):
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if next_line.strip() == "":
                    j += 1
                    continue
                if not next_line.startswith((" ", "\t")):
                    break
                j += 1
            block_lines = lines[i:j]
            tables_in_block: List[str] = []
            block_text = "\n".join(block_lines)
            for col_key in ("fromColumn", "toColumn"):
                for match in re.finditer(rf"{col_key}:\s*(.+?)(?:\r?\n|$)", block_text):
                    token = match.group(1).strip()
                    if "." in token:
                        table_name = token.split(".", 1)[0].strip()
                        if table_name:
                            tables_in_block.append(normalize_name(table_name) or table_name)
            blocks.append((i, j, sorted(set(tables_in_block))))
            i = j
            continue
        i += 1
    return blocks
