def main():
    import time
    from docling.document_converter import DocumentConverter

    from src.file_handling import file_location

    data = file_location.FolderPathOfASME()
    markdown_path = data.asme_jmd / 'markdown'
    pdf_path = data.asme_jmd_pdf
    pdf_path_list = pdf_path.rglob('*.pdf')


    converter = DocumentConverter().convert

    if not markdown_path.exists(): markdown_path.mkdir()

    export_times = []
    for pdf in pdf_path_list:
        if pdf.stem + '.md' not in [p.name for p in markdown_path.glob('*.md')]:
            start_time = time.time()
            doc = converter(pdf)
            file_export_path = markdown_path / (pdf.stem + '.md')
            md_content = doc.document.export_to_markdown()

            with open(file_export_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            elapsed = time.time() - start_time
            export_times.append(elapsed)
            print(f"Exported {pdf.stem + '.md'} in {elapsed:.2f}s")


if __name__ == "__main__":
    main()

