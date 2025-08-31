import sys
import os

def patch_sys_path():
    """
    Adds the project root to sys.path so imports like 'from src.xxx import yyy' work.
    Assumes this file lives in scripts/ and project root is one level up.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, ".."))

    if project_root not in sys.path:
        sys.path.insert(0, project_root)
