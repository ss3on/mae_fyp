import streamlit as st
from src.file_handling import file_location

file_structure = file_location.FileLocation()
page_path = file_structure.src / 'st_utils' /'pages'

def main_page():
    summary_page = st.Page(
        page = page_path / 'summary.py',
        title = 'Summary',
        icon = '📃',
        default = True
    )

    graphs_1_page = st.Page(
        page = page_path / 'graphs_1.py',
        title = 'Graph 1',
        icon = '📈'
    )

    pg = st.navigation(
        pages = {
            'Summary': [summary_page],
            'Graphs' : [graphs_1_page]
        },
        position = 'sidebar'
    )

    pg.run()


if __name__ == '__main__':
    main_page()