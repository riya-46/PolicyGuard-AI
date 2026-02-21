import streamlit as st
import pandas as pd
import time
import json
import tempfile

from pdf_processor import extract_text_from_pdf
from gemini_extractor import extract_rules_with_gemini
from rule_engine import apply_rules_to_dataset
from ml_model import apply_anomaly_detection
from risk_scoring import calculate_risk_score

st.set_page_config(page_title="PolicyGuard AI", layout="wide")

st.title("🔐 PolicyGuard AI - AML Compliance Monitoring System")

# -----------------------------
# File Upload Section
# -----------------------------

st.subheader("Upload AML Policy PDF")
policy_file = st.file_uploader("Upload Policy PDF", type=["pdf"])

st.subheader("Upload Transactions CSV")
transaction_file = st.file_uploader("Upload Transactions CSV", type=["csv"])

# -----------------------------
# Main Processing
# -----------------------------

if st.button("🚀 Run Compliance Analysis"):

    if policy_file is None or transaction_file is None:
        st.error("Please upload both Policy PDF and Transactions CSV.")
        st.stop()

    start_time = time.time()

    # -----------------------------------
    # STEP 1: Extract text from PDF
    # -----------------------------------

    policy_text = extract_text_from_pdf(policy_file)

    # -----------------------------------
    # STEP 2: Extract Rules from Gemini
    # -----------------------------------

    rules_json = extract_rules_with_gemini(policy_text)

    try:
        rules_list = json.loads(rules_json)
    except:
        st.error("❌ Gemini did not return valid JSON rules.")
        st.stop()

    st.subheader("📜 Extracted Rules")
    st.json(rules_list)

    # Save extracted rules for download
    rules_file = json.dumps(rules_list, indent=4)

    st.download_button(
        label="📥 Download Extracted Rules (JSON)",
        data=rules_file,
        file_name="extracted_rules.json",
        mime="application/json"
    )

    # -----------------------------------
    # STEP 3: Process Large CSV in Chunks
    # -----------------------------------

    chunks = pd.read_csv(transaction_file, chunksize=50000)

    processed_chunks = []
    total_rows = 0
    total_violations = 0
    total_anomalies = 0

    progress = st.progress(0)
    chunk_count = 0

    for chunk in chunks:

        # Apply Rules
        chunk = apply_rules_to_dataset(chunk, rules_list)

        # Apply Anomaly Detection
        chunk = apply_anomaly_detection(chunk)

        # Risk Scoring
        chunk = calculate_risk_score(chunk)

        # Count Stats
        total_rows += len(chunk)
        total_violations += (chunk["Violated_Rule"] != "").sum()
        total_anomalies += chunk["Anomaly_Flag"].sum()

        processed_chunks.append(chunk)

        chunk_count += 1
        progress.progress(min(chunk_count / 100, 1.0))

    df = pd.concat(processed_chunks, ignore_index=True)

    # -----------------------------------
    # STEP 4: High Risk Filtering
    # -----------------------------------

    high_risk_df = df[
        (df["Violated_Rule"] != "") |
        (df["Anomaly_Flag"] == True)
    ]

    st.success("✅ AML Analysis Completed Successfully!")

    # -----------------------------------
    # STEP 5: Display Only Top 100 (Avoid Crash)
    # -----------------------------------

    st.subheader("🔴 High Risk Transactions (Top 100 Only)")
    st.dataframe(high_risk_df.head(100))

    # -----------------------------------
    # STEP 6: Download Full High Risk CSV
    # -----------------------------------

    csv_data = high_risk_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="📥 Download All High Risk Transactions (CSV)",
        data=csv_data,
        file_name="all_high_risk_transactions.csv",
        mime="text/csv"
    )

    # -----------------------------------
    # STEP 7: Summary Panel
    # -----------------------------------

    end_time = time.time()

    st.subheader("📊 Analysis Summary")

    st.write("Total Rows Processed:", total_rows)
    st.write("Total Violations:", total_violations)
    st.write("Total Anomalies:", total_anomalies)
    st.write("⏱ Processing Time:", round(end_time - start_time, 2), "seconds")