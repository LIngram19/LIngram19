from pathlib import Path
import sys

PBIP_ROOT = Path(
    r"c:\Users\LINGRAM\Documents\PBI Test Files"
)

if len(sys.argv) > 1:
    REPORT_NAME = sys.argv[1]
else:
    REPORT_NAME = input(
        "PBIP Name: "
    ).strip()

MODEL_ROOT = (
    PBIP_ROOT
    / f"{REPORT_NAME}.SemanticModel"
)

REPORT_ROOT = (
    PBIP_ROOT
    / f"{REPORT_NAME}.Report"
)