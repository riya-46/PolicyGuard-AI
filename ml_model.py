from sklearn.ensemble import IsolationForest
import pandas as pd

def apply_anomaly_detection(df):

    df["Anomaly_Flag"] = False

    # Rename columns safely
    df.columns = df.columns.str.replace(" ", "_")

    required_cols = ["Amount_Received", "Amount_Paid"]

    for col in required_cols:
        if col not in df.columns:
            return df

    features = df[required_cols].fillna(0)

    model = IsolationForest(contamination=0.05, random_state=42)
    preds = model.fit_predict(features)

    df["Anomaly_Flag"] = preds == -1

    return df