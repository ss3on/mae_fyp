import time
from docling.document_converter import DocumentConverter

import bootstrap
bootstrap.patch_sys_path()
from src.file_handling import file_location


import telegram_update

notifier = telegram_update.TelegramNotifier(window_size=10)

def main():


    data = file_location.FolderPathOfASME()
    markdown_path = data.asme_jmd / 'markdown'
    pdf_path = data.asme_jmd_pdf


    converter = DocumentConverter().convert

    if not markdown_path.exists(): markdown_path.mkdir()

    export_times = []
    session_process_time :float = 0.0
    for pdf in pdf_path.rglob('*.pdf'):
        if pdf.stem + '.md' not in [p.name for p in markdown_path.glob('*.md')]:
            print(f'docling processing: {pdf.name}')
            start_time = time.time()
            doc = converter(pdf)
            file_export_path = markdown_path / (pdf.stem + '.md')
            md_content = doc.document.export_to_markdown()

            with open(file_export_path, "w", encoding="utf-8") as f:
                f.write(md_content)

            elapsed = time.time() - start_time
            session_process_time += elapsed
            export_times.append(elapsed)
            processed_message = f"Exported {pdf.stem + '.md'} in {elapsed:.2f}s. Session Total: {session_process_time:.2f}s"
            print(processed_message)
            notifier.add_message(processed_message)


if __name__ == "__main__":
    main()

