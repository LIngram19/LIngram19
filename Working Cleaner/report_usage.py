from __future__ import annotations

import json
from pathlib import Path

from report_usage_lib import collect_report_usage


if __name__ == "__main__":
    root = Path(r"c:\Users\LINGRAM\Documents\PBI Test Files")
    report_root = root / "5 Year Look Back.Report"

    usage = collect_report_usage(report_root)

    print("TABLES USED IN REPORT")
    for item in sorted(usage["tables"]):
        print(f"- {item}")
    print()

    print("COLUMNS USED IN REPORT")
    for item in sorted(usage["columns"]):
        print(f"- {item}")
    print()

    print("MEASURES USED IN REPORT")
    for item in sorted(usage["measures"]):
        print(f"- {item}")
