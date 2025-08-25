import time
import polars as pl
from pathlib import Path

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
        df = df.with_columns(
            (pl.col('article_url').str.split('.org').list.get(0) +
            pl.lit('.org') + pl.lit('.remotexs.ntu.edu.sg') +
             pl.col('article_url').str.split('.org').list.get(1)
             ).alias('article_url_remotexs')
        )
        return df

    cluster_url_by_issue_df = cluster_url_by_issue_remotexs(issues_dfs=all_issues_infor_df)
    cluster_url_by_issue_df.write_parquet(jmd_bare_paper_infor_path)
else:
    cluster_url_by_issue_df = pl.read_parquet(jmd_bare_paper_infor_path)




url_to_open_list = cluster_url_by_issue_df['doi'].to_list()
doi_filename_list = cluster_url_by_issue_df['doi_filename'].to_list()
article_html_folder :Path = asme_path.article_html

if not article_html_folder.exists(): article_html_folder.mkdir()

html_folder_paths_list = [article_html_folder / (doi_filename + '.html') for doi_filename in doi_filename_list]
test_pdf_url = url_to_open_list[0]

import undetected_chromedriver as webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

# login to remotexs
driver = webdriver.Chrome()
driver.get(test_pdf_url)

input('Press enter to continue...')

n :int = 0
for save_path, html_url in zip(html_folder_paths_list, url_to_open_list):
    if save_path.exists():
        continue
    try:
        driver.get(html_url)
        selector = "#Sidebar > div.sidebar-widget_wrap > div > div > div > div > div > div > div.widget-DynamicWidgetLayout"
        WebDriverWait(driver, 20).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        save_path.write_text(driver.page_source, encoding="utf-8")
        print(f'Saved to:  {save_path}')
    except Exception as e:
        print(f'Skipped saving {html_url} due to: {e}')

    time.sleep(1)

    n += 1
    if n % 10 == 0:
        time.sleep(5)

    if n % 50 == 0:
        time.sleep(60)
