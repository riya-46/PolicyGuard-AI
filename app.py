from gemini_extractor import extract_rules_with_gemini
from rule_engine import apply_rules_to_dataset
from ml_model import apply_anomaly_detection
from ml_model import apply_anomaly_detection, calculate_risk_score

import pandas as pd
import re

# -----------------------------------
# STEP 1: Sample Policy Text
# -----------------------------------

sample_text = """
Banks shall report suspicious transactions exceeding $10,000.
Financial institutions must monitor high frequency transfers.
"""

# -----------------------------------
# STEP 2: Extract Rules Using Gemini
# -----------------------------------

rules_json = extract_rules_with_gemini(sample_text)

print("\n===== RAW GEMINI OUTPUT =====")
print(rules_json)


# -----------------------------------
# STEP 3: Clean Gemini JSON Output
# -----------------------------------

def clean_json_string(text):
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)
    return text.strip()

cleaned_json = clean_json_string(rules_json)

print("\n===== CLEANED JSON =====")
print(cleaned_json)


# -----------------------------------
# STEP 4: Load Dataset
# -----------------------------------

df = pd.read_csv("sample_transactions.csv")

print("\n===== ORIGINAL DATASET =====")
print(df)


# -----------------------------------
# STEP 5: Apply Rule Engine
# -----------------------------------

df = apply_rules_to_dataset(df, cleaned_json)

print("\n===== AFTER RULE ENGINE =====")
print(df)


# -----------------------------------
# STEP 6: Apply ML Anomaly Detection
# -----------------------------------

df = apply_anomaly_detection(df)

print("\n===== AFTER ANOMALY DETECTION =====")
print(df)

df = calculate_risk_score(df)

print("\n===== FINAL RISK SCORING =====")
print(df)

# -----------------------------------
# STEP 7: Save Final Output
# -----------------------------------

df.to_csv("final_aml_output.csv", index=False)

print("\n✅ Full AML analysis completed.")
print("Output saved as final_aml_output.csv")