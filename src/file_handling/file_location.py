import os
from pathlib import Path
from dotenv import load_dotenv, set_key
from tkinter import Tk, filedialog

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


class FolderPathOfASME:
    def __init__(self, data: Path = None):
        if data is None:
            data = self.get_data_path_from_env()
        self.data = Path(data)
        self.asme_jmd = self.data / 'asme_jmd'
        self.asme_jmd_html_years = self.asme_jmd / 'html_years'
        self.asme_jmd_html_issues = self.asme_jmd / 'asme_issues'
        self.asme_jmd_pdf = self.asme_jmd / 'pdf'
        self.article_html = self.asme_jmd / 'article_html'

    def get_data_path_from_env(self):
        project_root = self.find_project_root()
        env_file = project_root / '.env'
        load_dotenv(dotenv_path=env_file)
        env_path = os.getenv('DATA_PATH')

        if env_path and Path(env_path).exists():
            return Path(env_path)
        else:
            print("DATA_PATH not set or invalid. Please select data folder.")

            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            selected_path = filedialog.askdirectory(title="Select Data Folder", parent=root)
            root.destroy()

            if not selected_path:
                raise ValueError("No folder selected")

            # Create .env if it doesn't exist and save the path
            if not env_file.exists():
                env_file.write_text("DATA_PATH=" + selected_path + "\n")

            # Update or add DATA_PATH in .env
            set_key(env_file, "DATA_PATH", selected_path)
            return Path(selected_path)

    def find_project_root(self, marker_folder="src"):
        path = Path.cwd()
        while path != path.parent:  # stop at filesystem root
            if (path / marker_folder).exists():
                return path
            path = path.parent
        return path