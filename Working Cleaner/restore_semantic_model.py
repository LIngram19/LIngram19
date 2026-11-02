from pathlib import Path
import shutil


from config import MODEL_ROOT

def find_latest_backup(model_root: Path) -> Path:
    backup_root = model_root.parent / "SemanticModelBackups"

    backups = sorted(
        backup_root.glob(model_root.name + "_backup_*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not backups:
        raise FileNotFoundError(
            f"No backup found in {backup_root}"
        )

    return backups[0]


def restore_semantic_model(model_root: Path) -> Path:
    backup_path = find_latest_backup(model_root)

    if model_root.exists():
        shutil.rmtree(model_root)

    shutil.copytree(
        backup_path,
        model_root,
    )

    return backup_path


def main():
    backup_used = restore_semantic_model(MODEL_ROOT)

    print()
    print("Semantic Model Restored")
    print(f"Backup Used : {backup_used}")
    print(f"Restored To : {MODEL_ROOT}")
    print()


if __name__ == "__main__":
    main()