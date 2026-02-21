from pdf_processor import extract_text_from_pdf

text = extract_text_from_pdf("policy.pdf")

print(len(text))

print(text[:24630])