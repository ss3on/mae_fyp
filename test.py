import polars as pl
import requests
from pathlib import Path
from selenium import webdriver

from src.file_handling import file_location
from src.web_scraping import asme_digitial_jmd

folder_path = file_location.FileLocation()
root_path = folder_path.root
data_path = root_path.parent.parent / 'fyp' / 'data'

asme_path = file_location.FolderPathOfASME(data_path)
asme_html_issues_path = asme_path.asme_jmd_html_issues
jmd_bare_paper_infor_path = asme_path.asme_jmd_pdf / 'jmd_papers_bare_infor.parquet'


if not jmd_bare_paper_infor_path.exists():
    all_issues_infor_df :pl.DataFrame = asme_digitial_jmd.all_issues_in_folder_to_df(asme_html_issues_path)

    def cluster_url_by_issue_remotexs(
            issues_dfs: pl.DataFrame
    )-> pl.DataFrame:
        df :pl.DataFrame = issues_dfs.select('year','volume','issue').unique(maintain_order=True)
        df = df.join(all_issues_infor_df, on=['year','volume','issue'])
        df = df.with_columns(
            (pl.col('pdf_url').str.split('.org').list.get(0) +
            pl.lit('.org') + pl.lit('.remotexs.ntu.edu.sg') +
             pl.col('pdf_url').str.split('.org').list.get(1)
             ).alias('pdf_url_remotexs')
        )
        return df

    cluster_url_by_issue_df = cluster_url_by_issue_remotexs(issues_dfs=all_issues_infor_df)
    cluster_url_by_issue_df.write_parquet(jmd_bare_paper_infor_path)
else:
    cluster_url_by_issue_df = pl.read_parquet(jmd_bare_paper_infor_path)


clustered_url_gte_2022_df = cluster_url_by_issue_df.filter(pl.col('year')>='2021')

url_to_open_list = clustered_url_gte_2022_df['pdf_url_remotexs'].to_list()
pdf_filename_list = clustered_url_gte_2022_df['pdf_filename'].to_list()
pdf_folder :Path = data_path / 'asme_jmd' / 'pdf'
if not pdf_folder.exists():
    pdf_folder.mkdir()
pdf_save_paths_list = [pdf_folder / pdf_filename for pdf_filename in pdf_filename_list]
test_pdf_url = url_to_open_list[0]



# login to remotexs
driver = webdriver.Chrome()
driver.get(test_pdf_url)

print('Please login to remotexs')
input("Press enter to continue...")

for save_path, pdf_url in zip(pdf_save_paths_list, url_to_open_list):
    if save_path.exists():
        continue
    driver.execute_script(f"window.open('{pdf_url}', '_blank');")
    driver.switch_to.window(driver.window_handles[-1])

    # Download original PDF with requests (session cookies preserved)
    cookies = {c['name']: c['value'] for c in driver.get_cookies()}
    r = requests.get(driver.current_url, cookies=cookies)
    save_path.write_bytes(r.content)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
