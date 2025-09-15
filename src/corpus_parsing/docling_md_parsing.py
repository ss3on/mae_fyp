import re

def remove_html_comments(text):
    return re.sub(r"<!--.*?-->", "", text)

def strip_markdown_syntax(text):
    text = re.sub(r"\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"`{1,3}.*?`{1,3}", "", text)
    text = re.sub(r"^```[\s\S]*?```", "", text, flags=re.MULTILINE)
    text = re.sub(r"[#*>_~\-]{2,}", "", text)
    return text

def normalize_whitespace(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\.{3,}", ".", text)
    text = re.sub(r"[^\w\s.,;:()\-]", "", text)
    return text.strip()

def extract_core_sections(text):
    start = re.search(r"^\s*##\s*\d*\s*(abstract|introduction)", text, re.IGNORECASE | re.MULTILINE)
    end = re.search(r"^\s*##\s*\d*\s*(references?|bibliography|acknowledgments?|funding|appendix|supplementary|conflict of interests?|authors? contributions)", text, re.IGNORECASE | re.MULTILINE)
    if start and end:
        return text[start.start():end.start()]
    elif start:
        return text[start.start():]
    elif end:
        return text[:end.start()]
    else:
        return text

def md_noise_reduction(raw_text):
    text = remove_html_comments(raw_text)
    text = extract_core_sections(text)
    text = strip_markdown_syntax(text)
    text = normalize_whitespace(text)
    return text