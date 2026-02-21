from gemini_extractor import extract_rules_with_gemini

sample_text = """
Banks shall report suspicious transactions exceeding $10,000.
Financial institutions must monitor high frequency transfers.
"""

rules = extract_rules_with_gemini(sample_text)

print(rules)