import time
from multiprocessing import Process
from docling.document_converter import DocumentConverter

import bootstrap
bootstrap.patch_sys_path()
from src.file_handling import file_location
import telegram_update

def get_unprocessed_pdfs(pdf_path, markdown_path):
    existing_md = {p.stem for p in markdown_path.glob('*.md')}
    return [pdf for pdf in pdf_path.rglob('*.pdf') if pdf.stem not in existing_md]

def process_batch(pdf_list, markdown_path):
    converter = DocumentConverter().convert
    notifier = telegram_update.TelegramNotifier(window_size=10)

    session_process_time = 0.0
    for pdf in pdf_list:
        print(f'docling processing: {pdf.name}')
        start_time = time.time()
        doc = converter(pdf)
        file_export_path = markdown_path / (pdf.stem + '.md')
        md_content = doc.document.export_to_markdown()

        with open(file_export_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        elapsed = time.time() - start_time
        session_process_time += elapsed
        processed_message = f"Exported {pdf.stem + '.md'} in {elapsed:.2f}s. Session Total: {session_process_time:.2f}s"
        print(processed_message)
        notifier.add_message(processed_message)

def main(simultaneous_run:int):
    data = file_location.FolderPathOfASME()
    markdown_path = data.asme_jmd / 'markdown'
    pdf_path = data.asme_jmd_pdf

    if not markdown_path.exists():
        markdown_path.mkdir()

    all_pdfs = get_unprocessed_pdfs(pdf_path, markdown_path)
    chunks = [all_pdfs[i::simultaneous_run] for i in range(simultaneous_run)]  # n-way round-robin split

    processes = [Process(target=process_batch, args=(chunk, markdown_path)) for chunk in chunks]

    for p in processes: p.start()
    for p in processes: p.join()

if __name__ == "__main__":
    main(simultaneous_run=3)
