from pathlib import Path

class FileLocation:
    def __init__(self):
        self.root = self.project_root()
        self.src = self.root / 'src'

    def project_root(self) -> Path:
        cur_path = Path.cwd()
        while cur_path != cur_path.parent:
            if (cur_path / "src").exists() and (cur_path / "src").is_dir():
                return cur_path
            cur_path = cur_path.parent
        raise FileNotFoundError("No 'src' folder found in parent directories.")


class FolderPathOfASME(FileLocation):
    def __init__(self, data :Path):
        super().__init__()
        self.data = data
        self.asme_jmd = self.data / 'asme_jmd'
        self.asme_jmd_html_years = self.asme_jmd / 'html_years'
        self.asme_jmd_html_issues = self.asme_jmd / 'asme_issues'
        self.asme_jmd_pdf = self.asme_jmd / 'pdf'
        self.article_html = self.asme_jmd / 'article_html'

