import time
import polars as pl
from pathlib import Path
from multiprocessing import Pool

from scripts import bootstrap
bootstrap.patch_sys_path()
from scripts import telegram_update

notifier = telegram_update.TelegramNotifier(window_size=1)

from src.corpus_parsing.docling_md_parsing import md_noise_reduction
from src.file_handling.file_location import FolderPathOfASME

folder_path = FolderPathOfASME()
keywords_folder_path = folder_path.asme_jmd / 'keywords'
keybert_bert_folder_path = keywords_folder_path / 'keybert_bert'
if not keywords_folder_path.exists(): keywords_folder_path.mkdir()
if not keybert_bert_folder_path.exists(): keybert_bert_folder_path.mkdir()

md_folder_path = folder_path.asme_jmd / 'markdown'


TOP_N = 50
NUM_CORES = 16
MODEL = "allenai/scibert_scivocab_uncased"


def init_worker():
    global kw_model
    from keybert import KeyBERT
    from sentence_transformers import SentenceTransformer
    sentence_model = SentenceTransformer(MODEL)
    kw_model = KeyBERT(model=sentence_model)


def extract_keywords_from_file(md_path):
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            doc = f.read()

        md_cleaned = md_noise_reduction(doc)

        keywords = kw_model.extract_keywords(
            md_cleaned,
            keyphrase_ngram_range=(1, 3),
            stop_words="english",
            top_n=TOP_N
        )
        return md_path.stem, keywords

    except Exception as e:
        return md_path.stem, f"ERROR: {e}"


def unprocessed_path(
        keywords_path: Path = keybert_bert_folder_path,
        md_path: Path = md_folder_path
):
    md_available = list(md_path.glob("*.md"))
    keywords_parquet_paths = list(keywords_path.glob("*.parquet"))

    if not keywords_parquet_paths:
        return md_available

    processed_md = set()
    for file in keywords_parquet_paths:
        df = pl.read_parquet(file, columns=["doi"])
        processed_md.update(df["doi"].to_list())

    unprocessed = [md for md in md_available if md.stem not in processed_md]
    return unprocessed


if __name__ == "__main__":

    session_process_time = 0.0

    batch_size = 100
    all_results = {}

    unprocessed_paths = unprocessed_path()
    parquet_files = [name.stem.split('_')[-1] for name in list(keybert_bert_folder_path.glob("*.parquet"))]
    last_batch_number = max([int(x) for x in parquet_files], default=0)


    with Pool(processes=NUM_CORES, initializer=init_worker) as pool:
        for i in range(0, len(unprocessed_paths), batch_size):

            start_time = time.time()

            batch_paths = unprocessed_paths[i:i + batch_size]
            results = pool.map(extract_keywords_from_file, batch_paths, chunksize=10)

            md_keywords = dict(results)

            batch_df = pl.DataFrame([
                {
                    "doi": doi,
                    "keywords": [kw for kw, _ in kw_items] if isinstance(kw_items, list) else [],
                    "scores": [score for _, score in kw_items] if isinstance(kw_items, list) else []
                }
                for doi, kw_items in md_keywords.items()
            ])

            export_batch_number = i // batch_size + 1 + last_batch_number

            batch_df.write_parquet(keybert_bert_folder_path / f"keywords_batch_{export_batch_number}.parquet")
            batch_message = f"Batch {export_batch_number} done."
            print(batch_message)

            elapsed = time.time() - start_time
            session_process_time += elapsed
            processed_message = f"{batch_message}  in {elapsed:.2f}s. Session Total: {session_process_time:.2f}s"
            notifier.add_message(processed_message)





