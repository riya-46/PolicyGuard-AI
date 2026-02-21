import streamlit as st
import pandas as pd
import time
import json
import tempfile
from gemini_extractor import extract_rules_with_gemini
from rule_engine import apply_rules_to_dataset
from ml_model import apply_anomaly_detection
from report_generator import generate_pdf_report
from pdf_processor import extract_text_from_pdf, clean_ocr_text

st.set_page_config(layout="wide")

st.title("🔐 PolicyGuard AI - AML Compliance Monitoring System")

# --------------------------
# SESSION STATE INIT
# --------------------------

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# --------------------------
# FILE UPLOAD
# --------------------------

policy_file = st.file_uploader("Upload AML Policy PDF", type=["pdf"])
transaction_file = st.file_uploader("Upload Transactions CSV", type=["csv"])

# --------------------------
# RUN ANALYSIS BUTTON
# --------------------------

if st.button("🚀 Run Compliance Analysis"):

    if policy_file and transaction_file:

        start_time = time.time()

        # Save temp PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(policy_file.read())
            temp_pdf_path = tmp.name

        # Extract text
        policy_text = extract_text_from_pdf(temp_pdf_path)
        policy_text = clean_ocr_text(policy_text)

        # Extract rules using Gemini
        rules_json = extract_rules_with_gemini(policy_text)

        try:
            rules_list = json.loads(rules_json)
        except:
            st.error("Gemini did not return valid JSON rules.")
            st.stop()

        # --------------------------
        # CHUNK PROCESSING (FULL DATASET)
        # --------------------------

        chunks = pd.read_csv(transaction_file, chunksize=50000)

        processed_chunks = []
        total_rows = 0

        for chunk in chunks:
            chunk = apply_rules_to_dataset(chunk, rules_list)
            chunk = apply_anomaly_detection(chunk)

            processed_chunks.append(chunk)
            total_rows += len(chunk)

        df = pd.concat(processed_chunks, ignore_index=True)

        end_time = time.time()

        # --------------------------
        # SAVE TO SESSION STATE
        # --------------------------

        st.session_state.df = df
        st.session_state.rules = rules_list
        st.session_state.total_rows = total_rows
        st.session_state.processing_time = round(end_time - start_time, 2)
        st.session_state.analysis_done = True

        st.success("✅ AML Analysis Completed Successfully!")

# =====================================================
# DISPLAY RESULTS (AFTER ANALYSIS)
# =====================================================

if st.session_state.analysis_done:

    df = st.session_state.df
    rules_list = st.session_state.rules

    # --------------------------
    # HIGH RISK FILTER
    # --------------------------

    high_risk_df = df[
        (df["Violated_Rule"] != "") |
        (df["Anomaly_Flag"] == True)
    ]

    st.subheader("🔴 High Risk Transactions (Top 100 Only)")
    st.dataframe(high_risk_df.head(100))

    # --------------------------
    # DOWNLOAD ALL HIGH RISK CSV
    # --------------------------

    csv_data = high_risk_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Download All High Risk Transactions (CSV)",
        data=csv_data,
        file_name="high_risk_transactions.csv",
        mime="text/csv"
    )

    # --------------------------
    # DOWNLOAD FULL PDF REPORT
    # --------------------------

    pdf_file = generate_pdf_report(high_risk_df)

    st.download_button(
        "⬇ Download Full High Risk Report (PDF)",
        data=pdf_file,
        file_name="high_risk_report.pdf",
        mime="application/pdf"
    )

    # --------------------------
    # DOWNLOAD EXTRACTED RULES
    # --------------------------

    rules_json_download = json.dumps(rules_list, indent=4)

    st.download_button(
        "⬇ Download Extracted Rules (JSON)",
        data=rules_json_download,
        file_name="extracted_rules.json",
        mime="application/json"
    )

    # --------------------------
    # SUMMARY PANEL
    # --------------------------

    st.subheader("📊 Analysis Summary")

    st.write("Total Rows Processed:", st.session_state.total_rows)
    st.write("Total Violations:", (df["Violated_Rule"] != "").sum())
    st.write("Total Anomalies:", df["Anomaly_Flag"].sum())
    st.write("⏱ Processing Time:", st.session_state.processing_time, "seconds")