import re
from pathlib import Path

import polars as pl
from bs4 import BeautifulSoup

from ..file_handling import file_location

main_url :str = r'https://asmedigitalcollection.asme.org/'

def issue_article_scrap(article_soup :BeautifulSoup, articles_to_append: dict) -> dict:
    title = article_soup.select('div.al-article-items > h5 > a[href]')[0].text
    authors_html = article_soup.select('div.al-authors-list > span.wi-fullname > a[href]')
    authors :str = ';'.join([author.text.strip() for author in authors_html])
    doi_link :str = article_soup.select('div.ww-citation-primary > span.citation-label > a[href]')[0].get('href')
    journal_publish_infor_line :list = article_soup.select('div.pub-history-row > div.ww-citation-primary')[0].text.strip().split('\n')[0].split('.')
    journal_publish_infor :str = find_year_text(journal_publish_infor_line)
    year :str = journal_publish_infor.split(',')[0].split(' ')[1]
    month :str = journal_publish_infor.split(',')[0].split(' ')[0]
    volume :str = journal_publish_infor.split(',')[1].strip().split('(')[0]
    issue :str = journal_publish_infor.split(',')[1].strip().split('(')[1].split(')')[0]
    article_url :str = main_url + article_soup.select('div.item > a.viewArticleLink')[0].get('href')
    pdf_url :str =  main_url[:-1] + article_soup.select('div.resource-links-info > div.item > a.pdf')[0].get('href')
    topics :str = ';'.join([topics_ahref.text.strip() for topics_ahref in article_soup.select('div.al-terms-wrapper > span > a')])

    articles_to_append['title'] += [title]
    articles_to_append['authors'] += [authors]
    articles_to_append['doi'] += [doi_link]
    articles_to_append['year'] += [year]
    articles_to_append['month'] += [month]
    articles_to_append['volume'] += [volume]
    articles_to_append['issue'] += [issue]
    articles_to_append['article_url'] += [article_url]
    articles_to_append['pdf_url'] += [pdf_url]
    articles_to_append['topics'] += [topics]
    return articles_to_append


def find_year_text(split_list :list)->str:
    split_list = [text.strip() for text in split_list]
    for text in split_list:
        if re.findall(r'\b(19[0-9]{2}|20[0-9]{2})', text):
            return text
    return ''

def issue_page_scrap(issue_soup :BeautifulSoup) -> dict:
    issues_columns :tuple = ('title', 'authors', 'doi', 'year', 'month','volume', 'issue', 'article_url', 'pdf_url','topics')
    issue_articles_infor :dict = {key:[] for key in issues_columns}
    for article in issue_soup.select('div.al-article-item-wrap.al-normal'):
        issue_articles_infor :dict = issue_article_scrap(article, issue_articles_infor)
    return issue_articles_infor


def issue_html_to_df(issue_path :Path)->pl.DataFrame:
    with open(issue_path) as issue_file:
        soup :BeautifulSoup = BeautifulSoup(issue_file, 'lxml')
    articles_infor :dict = issue_page_scrap(soup)
    articles_infor_df :pl.DataFrame = pl.DataFrame(articles_infor)
    return articles_infor_df

def all_issues_in_folder_to_df(folder_path :Path)->pl.DataFrame:
    html_path_map :map = folder_path.glob('*.html')
    html_path_list :list = [html for html in html_path_map]
    html_path_list.sort()
    dfs :list = [issue_html_to_df(html_path) for html_path in html_path_list]
    df = pl.concat(dfs)
    df = df.with_columns(
        (pl.col('volume') + pl.lit('_') + pl.col('issue') + pl.lit('_') + pl.col('title') + pl.lit('.pdf')).alias('pdf_filename'),
    )
    return df