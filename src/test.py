import polars as pl
from pathlib import Path

from file_handling import file_location
from src.file_handling.file_location import FolderPathOfASME

asme_path = FolderPathOfASME()
asme_issues_paths = asme_path.asme_jmd_html_issues.glob("*.html")
asme_issues = [html for html in asme_issues_paths]
print(asme_issues)