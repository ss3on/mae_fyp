from src.file_handling import file_location
folder_path = file_location.FolderPathOfASME()
md_path = folder_path.asme_jmd / 'markdown'


from keybert import KeyBERT

model_name = "allenai/specter2_base"
kw_model = KeyBERT(model=model_name)


test_mds = list(md_path.glob("*.md"))[:10]
test_results = {}
print(test_mds)

for md in test_mds:
    with open(md, "r", encoding="utf-8") as f:
        doc = f.read()
    keywords = kw_model.extract_keywords(
        doc,
        keyphrase_ngram_range=(1, 3),
        stop_words="english",
        top_n=30
    )
    test_results[md.stem] = keywords

print(test_results)
