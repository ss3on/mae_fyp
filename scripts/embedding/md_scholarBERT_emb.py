import torch
from transformers import AutoTokenizer, AutoModel
from markdownify import markdownify as md_to_text
import time

import bootstrap
bootstrap.patch_sys_path()
from src.file_handling import file_location

import telegram_update
notifier = telegram_update.TelegramNotifier(window_size=1000)

data = file_location.FolderPathOfASME()
data_path = data.data
md_path = data.asme_jmd / 'markdown'
embeddings_path = data.asme_jmd / 'embeddings' / 'fp16'
if not embeddings_path.exists(): embeddings_path.mkdir()

tokenizer = AutoTokenizer.from_pretrained("globuslabs/ScholarBERT-XL", add_pooling_layer=False)
model = AutoModel.from_pretrained("globuslabs/ScholarBERT-XL" , dtype=torch.float16).to("cuda")
model.eval()


def get_embedding(texts, model, tokenizer):
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True).to("cuda")
    with torch.no_grad():
        outputs = model(**inputs)
        pooled = outputs.last_hidden_state.mean(dim=1).cpu()
    return pooled


def save_embedding(doi, embeddings):
    with open(embeddings_path / f"{doi}.pt", "wb") as f:
        torch.save(embeddings, f)



session_process_time :float = 0.0
for md in md_path.glob("*.md"):
    start_time = time.time()
    doi = md.stem
    if doi + ".pt" in [p.name for p in embeddings_path.rglob("*.pt")]:
        continue
    with open(md, "r", encoding="utf-8") as f:
        text = md_to_text(f.read())
    embeddings = get_embedding([text], model, tokenizer)
    save_embedding(doi, embeddings)

    elapsed = time.time() - start_time
    session_process_time += elapsed
    processed_message = f"Exported {doi + '.pt'} in {elapsed:.2f}s. Session Total: {session_process_time:.2f}s"
    print(processed_message)
    notifier.add_message(processed_message)