from pathlib import Path
import shutil


MODEL_ROOT = Path(
    r"c:\Users\LINGRAM\Documents\PBI Test Files\5 Year Look Back.SemanticModel"
)


def backup_semantic_model(model_root: Path) -> Path:
    backup_root = model_root.parent / "SemanticModelBackups"
    backup_root.mkdir(exist_ok=True)

    # Remove existing backups for this model
    for existing_backup in backup_root.glob(model_root.name + "_backup_*"):
        if existing_backup.is_dir():
            shutil.rmtree(existing_backup)
        else:
            existing_backup.unlink(missing_ok=True)

    backup_path = (
        backup_root
        / f"{model_root.name}_backup_{int(model_root.stat().st_mtime)}"
    )

    shutil.copytree(
        model_root,
        backup_path,
        dirs_exist_ok=True,
    )

    return backup_path


def main():
    backup_path = backup_semantic_model(MODEL_ROOT)

    print()
    print("Backup Created")
    print(f"Source : {MODEL_ROOT}")
    print(f"Backup : {backup_path}")
    print()


if __name__ == "__main__":
    main()