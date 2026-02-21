import pandas as pd


def calculate_risk_score(df):

    risk_scores = []

    for _, row in df.iterrows():

        score = 0

        # Rule violation weight
        if pd.notna(row.get("Violated_Rule")) and row["Violated_Rule"] != "":
            score += 50

        # Suspicious flag weight
        if row.get("Is_Suspicious") == True:
            score += 20

        # High amount weight
        if row.get("Amount", 0) > 100000:
            score += 10

        # Anomaly detection weight
        if row.get("Anomaly_Flag") == True:
            score += 20

        risk_scores.append(score)

    df["Risk_Score"] = risk_scores

    # Assign Risk Level
    def assign_level(score):
        if score >= 80:
            return "High"
        elif score >= 50:
            return "Medium"
        else:
            return "Low"

    df["Risk_Level"] = df["Risk_Score"].apply(assign_level)

    return df