KEYWORDS = [
    "shall",
    "must",
    "required",
    "report",
    "threshold",
    "exceed",
    "suspicious"
]

def extract_keyword_rules(paragraphs):
    matched = []

    for para in paragraphs:
        for keyword in KEYWORDS:
            if keyword.lower() in para.lower():
                matched.append(para.strip())
                break

    return matched