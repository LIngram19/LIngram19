import argparse
import shutil
from pathlib import Path


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--root",
        required=True
    )

    parser.add_argument(
        "--report",
        required=True
    )

    parser.add_argument(
        "--backup",
        required=True
    )

    args = parser.parse_args()

    semantic_model = (
        Path(args.root)
        / f"{args.report}.SemanticModel"
    )

    backup_folder = (
        Path(args.root)
        / "_cleanup_backup"
        / args.backup
    )

    definition = (
        semantic_model
        / "definition"
    )

    shutil.copy2(
        backup_folder
        / "relationships.tmdl",
        definition
        / "relationships.tmdl"
    )

    shutil.copy2(
        backup_folder
        / "expressions.tmdl",
        definition
        / "expressions.tmdl"
    )

    tables_target = (
        definition
        / "tables"
    )

    if tables_target.exists():

        shutil.rmtree(
            tables_target
        )

    shutil.copytree(
        backup_folder
        / "tables",
        tables_target
    )

    print(
        "Restore Complete"
    )


if __name__ == "__main__":
    main() 