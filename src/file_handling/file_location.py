from pathlib import Path

class FileLocation:
    def __init__(self):
        self.src = Path.cwd()
        self.main_dir = self.src.parent
        self.data = self.main_dir / 'data'

class FolderPathOfASME(FileLocation):
    def __init__(self):
        super().__init__()
        self.asme_jmd = self.data / 'asme_jmd'
        self.asme_jmd_html_years = self.asme_jmd / 'html_years'
        self.asme_jmd_html_issues = self.data / 'asme_issues'
        self.asme_jmd_pdf = self.asme_jmd / 'pdf'