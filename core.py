
from pathlib import Path
import shutil


def assert_path(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"'{path}' does not exist.")

class Directory:
    def __init__(self, base: str, target: str = None):
        self.base = Path(base).resolve()
        assert_path(self.base)
        
        # Logic: If target is provided, use it. Otherwise default to sibling __patch
        if target:
            self.base_patch = Path(target).resolve()
        else:
            _base = self.base
            self.base_patch = self.base.with_name(_base.name + "__patch")

    def copy_item(self, path: str):
        src = Path(path).resolve()
        self.is_within_base(src)
        
        # Calculate destination path maintaining structure
        rel_path = src.relative_to(self.base)
        dst = self.base_patch / rel_path
        
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return dst

    def move_item(self, path: str):
        src = Path(path).resolve()
        self.is_within_base(src)
        
        rel_path = src.relative_to(self.base)
        dst = self.base_patch / rel_path
        
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
            shutil.rmtree(src)
        elif src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            src.unlink()
        return dst

    def is_within_base(self, path: Path):
        # Resolve both to ensure we are comparing absolute paths
        if not path.resolve().is_relative_to(self.base):
            raise ValueError(f"'{path.name}' is not inside base directory '{self.base}'.")


