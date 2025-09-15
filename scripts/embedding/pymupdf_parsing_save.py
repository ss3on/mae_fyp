import pymupdf

import time
from scripts import bootstrap
bootstrap.patch_sys_path()

from scripts import telegram_update
notifier = telegram_update.TelegramNotifier(window_size=1000)

session_process_time :float = 0.0

from src.file_handling import file_location

data = file_location.FolderPathOfASME()
pdf_path = data.asme_jmd_pdf
pymupdf_text_path = data.asme_jmd / 'pymupdf_text'

for pdf in pdf_path.rglob('*.pdf'):
    start_time = time.time()
    doi = pdf.stem
    txt_path = pymupdf_text_path / (doi + '.txt')
    if pdf.stem not in [txt.stem for txt in pymupdf_text_path.rglob('*.txt')]:
        with pymupdf.open(pdf) as doc:
            text = ''.join(page.get_text('text') for page in doc)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)


    elapsed = time.time() - start_time
    session_process_time += elapsed
    processed_message = f"pymupdf Exported {doi + '.txt'} in {elapsed:.2f}s. Session Total: {session_process_time:.2f}s"
    print(processed_message)
    notifier.add_message(processed_message)